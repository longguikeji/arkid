'''
SAML IdP config
'''
import os
from django.conf import settings
from django.urls import reverse
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT,NAMEID_FORMAT_ENCRYPTED
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT

from arkid.config import get_app_config

from ..common.certs import BASEDIR as CERT_BASEDIR
from ..common.metadata import BASEDIR as MD_BASEDIR


def get_saml_idp_config(tenant_uuid, config_id, namespace=""):
    """
    创建SAML_IDP_CONFIG
    """
    sp_metadata_path = os.path.join(MD_BASEDIR, f'{tenant_uuid}_{config_id}_sp.xml')
    
    local_sp_metadata = [sp_metadata_path] if os.path.exists(sp_metadata_path) else []
    
    saml_idp_config = {
        'debug': settings.DEBUG,
        'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
        'entityid': f'{get_app_config().get_frontend_host()}{reverse(f"{namespace}:idp_metadata",args=(tenant_uuid,config_id))}',
        'description':
        'longguikeji IdP setup',
        'service': {
            'idp': {
                'name': 'Django localhost IdP',
                'endpoints': {
                    'single_sign_on_service': [
                        (f'{get_app_config().get_host()}{reverse(f"{namespace}:idp_sso_post",args=(tenant_uuid,config_id))}', BINDING_HTTP_POST),
                        (f'{get_app_config().get_frontend_host()}{reverse(f"{namespace}:idp_sso_post",args=(tenant_uuid,config_id))}', BINDING_HTTP_POST),
                        (f'{get_app_config().get_host()}{reverse(f"{namespace}:idp_sso_redirect",args=(tenant_uuid,config_id))}', BINDING_HTTP_REDIRECT),
                        (f'{get_app_config().get_frontend_host()}{reverse(f"{namespace}:idp_sso_redirect",args=(tenant_uuid,config_id))}', BINDING_HTTP_REDIRECT),
                    ],
                },
                'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT,NAMEID_FORMAT_ENCRYPTED],
                'sign_response': False,
                'sign_assertion': False,
            },
        },
        'metadata': {
            'local': local_sp_metadata,
        },
        # Signing
        'key_file': os.path.join(CERT_BASEDIR,f'{tenant_uuid}.key'),
        'cert_file': os.path.join(CERT_BASEDIR,f'{tenant_uuid}.crt'),
        # Encryption
        'encryption_keypairs': [{
            'key_file': os.path.join(CERT_BASEDIR,f'{tenant_uuid}.key'),
            'cert_file': os.path.join(CERT_BASEDIR,f'{tenant_uuid}.crt'),
        }],
        'valid_for': 365 * 24,
    }
    return saml_idp_config
