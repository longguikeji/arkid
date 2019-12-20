'''
SAML IdP config
'''
import os
from django.conf import settings
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT

# djangosaml2idp config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAML_IDP_CONFIG = {
    'debug' : settings.DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
    'entityid': '%s/saml/metadata' % settings.BASE_URL,
    'description': 'longguikeji IdP setup',

    'service': {
        'idp': {
            'name': 'Django localhost IdP',
            'endpoints': {
                'single_sign_on_service': [
                    ('%s/saml/sso/post' % settings.BASE_URL, BINDING_HTTP_POST),
                    ('%s/saml/sso/redirect' % settings.BASE_URL, BINDING_HTTP_REDIRECT),
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
            'sign_response': False,
            'sign_assertion': False,
        },
    },

    'metadata': {
        'local': [os.path.join(os.path.join(os.path.join(BASE_DIR, 'djangosaml2idp'),\
            'saml2_config'), f) for f in os.listdir(BASE_DIR+'/djangosaml2idp/saml2_config/')\
                if f.split('.')[-1] == 'xml'],
    },
    # Signing
    'key_file': BASE_DIR + '/djangosaml2idp/certificates/mykey.pem',
    'cert_file': BASE_DIR + '/djangosaml2idp/certificates/mycert.pem',
    # Encryption
    'encryption_keypairs': [{
        'key_file': BASE_DIR + '/djangosaml2idp/certificates/mykey.pem',
        'cert_file': BASE_DIR + '/djangosaml2idp/certificates/mycert.pem',
    }],
    'valid_for': 365 * 24,
}
