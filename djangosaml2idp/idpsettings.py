'''
SAML IdP config
'''
import os
from django.conf import settings
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from config import get_app_config

# djangosaml2idp config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_SAML_IDP_CONFIG(tenant_uuid):
    BASE_URL = f"{get_app_config().get_host()}/api/v1/tenant/{tenant_uuid}"
    SAML_IDP_CONFIG = {
        'debug':
        settings.DEBUG,
        'xmlsec_binary':
        get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
        'entityid':
        '%s/metadata/' % BASE_URL,
        'description':
        'longguikeji IdP setup',
        'service': {
            'idp': {
                'name': 'Django localhost IdP',
                'endpoints': {
                    'single_sign_on_service': [
                        ('%s/sso/post/' % BASE_URL, BINDING_HTTP_POST),
                        ('%s/sso/redirect/' % BASE_URL, BINDING_HTTP_REDIRECT),
                    ],
                },
                'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
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
        'key_file':
        BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_key.pem',
        'cert_file':
        BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_cert.pem',
        # Encryption
        'encryption_keypairs': [{
            'key_file': BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_key.pem',
            'cert_file': BASE_DIR + f'/djangosaml2idp/certificates/{tenant_uuid}_cert.pem',
        }],
        'valid_for':
        365 * 24,
    }
    return SAML_IDP_CONFIG
