# Copyright (C) 2012 Yaco Sistemas (http://www.yaco.es)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import base64
import logging
import re
import urllib
import zlib
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from saml2.config import SPConfig
from saml2.s_utils import UnknownSystemEntity


logger = logging.getLogger(__name__)


def get_custom_setting(name: str, default=None):
    return getattr(settings, name, default)


def available_idps(config: SPConfig, langpref=None) -> dict:
    if langpref is None:
        langpref = "en"

    idps = set()

    for metadata_name, metadata in config.metadata.metadata.items():
        result = metadata.any('idpsso_descriptor', 'single_sign_on_service')
        if result:
            idps.update(result.keys())

    return {
        idp: config.metadata.name(idp, langpref)
        for idp in idps
    }


def get_idp_sso_supported_bindings(idp_entity_id: Optional[str] = None, config: Optional[SPConfig] = None) -> list:
    """Returns the list of bindings supported by an IDP
    This is not clear in the pysaml2 code, so wrapping it in a util"""
    if config is None:
        # avoid circular import
        from .conf import get_config
        config = get_config()
    # load metadata store from config
    meta = getattr(config, 'metadata', {})
    # if idp is None, assume only one exists so just use that
    if idp_entity_id is None:
        try:
            idp_entity_id = list(available_idps(config).keys())[0]
        except IndexError:
            raise ImproperlyConfigured("No IdP configured!")
    try:
        return list(meta.service(idp_entity_id, 'idpsso_descriptor', 'single_sign_on_service').keys())
    except UnknownSystemEntity:
        raise UnknownSystemEntity
    except Exception as e:
        logger.error(f"get_idp_sso_supported_bindings failed with: {e}")

def get_location(http_info):
    """Extract the redirect URL from a pysaml2 http_info object"""
    try:
        headers = dict(http_info['headers'])
        return headers['Location']
    except KeyError:
        return http_info['url']


def get_fallback_login_redirect_url():
    login_redirect_url = get_custom_setting('LOGIN_REDIRECT_URL', '/')
    return resolve_url(get_custom_setting('ACS_DEFAULT_REDIRECT_URL', login_redirect_url))


def validate_referral_url(request, url):
    # Ensure the user-originating redirection url is safe.
    # By setting SAML_ALLOWED_HOSTS in settings.py the user may provide a list of "allowed"
    # hostnames for post-login redirects, much like one would specify ALLOWED_HOSTS .
    # If this setting is absent, the default is to use the hostname that was used for the current
    # request.
    saml_allowed_hosts = set(
        getattr(settings, 'SAML_ALLOWED_HOSTS', [request.get_host()]))

    if not is_safe_url(url=url, allowed_hosts=saml_allowed_hosts):
        return get_fallback_login_redirect_url()
    return url


def saml2_from_httpredirect_request(url):
    urlquery = urllib.parse.urlparse(url).query
    b64_inflated_saml2req = urllib.parse.parse_qs(urlquery)['SAMLRequest'][0]

    inflated_saml2req = base64.b64decode(b64_inflated_saml2req)
    deflated_saml2req = zlib.decompress(inflated_saml2req, -15)
    return deflated_saml2req


def get_session_id_from_saml2(saml2_xml):
    saml2_xml = saml2_xml.decode() if isinstance(saml2_xml, bytes) else saml2_xml
    return re.findall(r'ID="([a-z0-9\-]*)"', saml2_xml, re.I)[0]


def get_subject_id_from_saml2(saml2_xml):
    saml2_xml = saml2_xml if isinstance(saml2_xml, str) else saml2_xml.decode()
    re.findall('">([a-z0-9]+)</saml:NameID>', saml2_xml)[0]


def add_param_in_url(url: str, param_key: str, param_value: str):
    params = list(url.split('?'))
    params.append(f'{param_key}={param_value}')
    new_url = params[0] + '?' + ''.join(params[1:])
    return new_url


def add_idp_hinting(request, http_response) -> bool:
    idphin_param = getattr(settings, 'SAML2_IDPHINT_PARAM', 'idphint')
    urllib.parse.urlencode(request.GET)

    if idphin_param not in request.GET.keys():
        return False

    idphint = request.GET[idphin_param]
    # validation : TODO -> improve!
    if idphint[0:4] != 'http':
        logger.warning(
            f'Idp hinting: "{idphint}" doesn\'t contain a valid value.'
            'idphint paramenter ignored.'
        )
        return False

    if http_response.status_code in (302, 303):
        # redirect binding
        # urlp = urllib.parse.urlparse(http_response.url)
        new_url = add_param_in_url(http_response.url,
                                   idphin_param, idphint)
        return HttpResponseRedirect(new_url)

    elif http_response.status_code == 200:
        # post binding
        res = re.search(r'action="(?P<url>[a-z0-9\:\/\_\-\.]*)"',
                        http_response.content.decode(), re.I)
        if not res:
            return False
        orig_url = res.groupdict()['url']
        #
        new_url = add_param_in_url(orig_url, idphin_param, idphint)
        content = http_response.content.decode()\
                               .replace(orig_url, new_url)\
                               .encode()
        return HttpResponse(content)

    else:
        logger.warning(
            f'Idp hinting: cannot detect request type [{http_response.status_code}]'
        )
    return False
