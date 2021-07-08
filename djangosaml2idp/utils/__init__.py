import base64
import datetime
import xml.dom.minidom
from saml2.response import StatusResponse
import xml.etree.ElementTree as ET
import zlib
from xml.parsers.expat import ExpatError
from django.conf import settings
from django.utils.timezone import now, is_naive, make_aware
from django.utils.translation import gettext as _
import arrow
import requests
from django.core.exceptions import ValidationError
from .store_params_in_session import store_params_in_session
from .sso_entry import sso_entry
from .repr_saml import repr_saml


def encode_saml(saml_envelope: str, use_zlib: bool = False) -> bytes:
    # Not sure where 2:-4 came from, but that's how pysaml2 does it, and it works
    before_base64 = zlib.compress(saml_envelope.encode())[2:-4] if use_zlib else saml_envelope.encode()
    return base64.b64encode(before_base64)


def verify_request_signature(req_info: StatusResponse) -> None:
    """ Signature verification for authn request signature_check is at
        saml2.sigver.SecurityContext.correctly_signed_authn_request
    """
    if not req_info.signature_check(req_info.xmlstr):
        raise ValueError(_("Message signature verification failure"))


def fetch_metadata(remote_metadata_url: str) -> str:
    ''' Fetch remote metadata. Raise a ValidationError if it could not successfully fetch something from the url '''
    try:
        content = requests.get(remote_metadata_url, timeout=(3, 10))
        if content.status_code != 200:
            raise Exception(f'Non-successful request, received status code {content.status_code}')
    except Exception as e:
        raise ValidationError(f'Could not fetch metadata from {remote_metadata_url}: {e}')
    return content.text


def validate_metadata(metadata: str) -> str:
    ''' Validate if the given metadata is valid xml, raise a ValidationError otherwise. Returns the metadata string back.
    '''
    try:
        ET.fromstring(metadata)
    except Exception as e:
        raise ValidationError(f'Metadata is not valid metadata xml: {e}')
    return metadata


def extract_validuntil_from_metadata(metadata: str) -> datetime.datetime:
    ''' Extract the ValidUntil timestamp from the given metadata. Returns that timestamp if successfully, raise a ValidationError otherwise.
    '''
    try:
        metadata_expiration_dt = arrow.get(ET.fromstring(metadata).attrib['validUntil']).datetime
    except Exception as e:
        fallback = getattr(settings, "SAML_IDP_FALLBACK_EXPIRATION_DAYS", 0)
        if fallback:
            return now() + datetime.timedelta(days=fallback)
        raise ValidationError(f'Could not extra ValidUntil timestamp from metadata: {e}')

    if not settings.USE_TZ:
        return metadata_expiration_dt.replace(tzinfo=None)
    if is_naive(metadata_expiration_dt):
        return make_aware(metadata_expiration_dt)
    return metadata_expiration_dt
