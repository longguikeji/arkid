'''
SAML IdP config
'''
import os
from django.conf import settings
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED,NAMEID_FORMAT_TRANSIENT
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from config import get_app_config

# djangosaml2idp config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_saml_idp_config(tenant_uuid,app_id):
    """
    创建SAML_IDP_CONFIG
    """
    baseurl = f"{get_app_config().get_host()}/api/v1/tenant/{tenant_uuid}/app/{app_id}"
    saml_idp_config = {
        'debug': settings.DEBUG,
        'xmlsec_binary':get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
        'entityid': '%s/metadata/' % baseurl,
        'description':
        'longguikeji IdP setup',
        'service': {
            'idp': {
                'name': 'Django localhost IdP',
                'endpoints': {
                    'single_sign_on_service': [
                        ('%s/sso/post/' % baseurl, BINDING_HTTP_POST),
                        ('%s/sso/redirect/' % baseurl, BINDING_HTTP_REDIRECT),
                    ],
                },
                'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT],
                'sign_response': False,
                'sign_assertion': False,
            },
        },
        'metadata': {
            'local': [
                os.path.join(os.path.join(os.path.join(BASE_DIR, 'djangosaml2idp'), 'saml2_config'), f)
                for f in os.listdir(BASE_DIR + '/djangosaml2idp/saml2_config/') if f.split('.')[-1] == 'xml'
            ],
        },
        # Signing
        'key_file':BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_key.pem',
        'cert_file':BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_cert.pem',
        # Encryption
        'encryption_keypairs': [{
            'key_file': BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_key.pem',
            'cert_file': BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_cert.pem',
        }],
        'valid_for': 365 * 24,
    }
    return saml_idp_config
