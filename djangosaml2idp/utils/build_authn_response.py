"""
SAML2.0协议构建response
"""

import logging
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED, NameID
from djangosaml2idp.idp import IDP
from djangosaml2idp.processors import BaseProcessor

logger = logging.getLogger(__name__)

def build_authn_response(tenant__uuid, app_id, user, authn, resp_args, service_provider) -> list:  # type: ignore
    """ pysaml2 server.Server.create_authn_response wrapper
    """
    policy = resp_args.get('name_id_policy', None)
    if policy is None:
        name_id_format = NAMEID_FORMAT_UNSPECIFIED
    else:
        name_id_format = policy.format

    idp_server = IDP.load(tenant__uuid, app_id)
    idp_name_id_format_list = idp_server.config.getattr(
        "name_id_format",
        "idp"
    ) or [NAMEID_FORMAT_UNSPECIFIED]

    if name_id_format not in idp_name_id_format_list:
        raise ImproperlyConfigured(
            _('SP requested a name_id_format that is not supported in the IDP: {}').format(name_id_format))

    processor: BaseProcessor = service_provider.processor  # type: ignore
    user_id = processor.get_user_id(
        user, name_id_format, service_provider, idp_server.config)
    name_id = NameID(format=name_id_format,
                        sp_name_qualifier=service_provider.entity_id, text=user_id)

    return idp_server.create_authn_response(
        authn=authn,
        identity=processor.create_identity(
            user, service_provider.attribute_mapping),
        name_id=name_id,
        userid=user_id,
        sp_entity_id=service_provider.entity_id,
        # Signing
        sign_response=service_provider.sign_response,
        sign_assertion=service_provider.sign_assertion,
        sign_alg=service_provider.signing_algorithm,
        digest_alg=service_provider.digest_algorithm,
        # Encryption
        encrypt_assertion=service_provider.encrypt_saml_responses,
        encrypted_advice_attributes=service_provider.encrypt_saml_responses,
        **resp_args
    )
