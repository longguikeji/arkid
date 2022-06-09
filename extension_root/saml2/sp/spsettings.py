'''
SAML SP config
'''
import os
from django.conf import settings
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from config import get_app_config

# djangosaml2SP config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_saml_sp_config(tenant_uuid):
    """
    创建SAML_SP_CONFIG
    """
    baseurl = f"{get_app_config().get_host()}/api/v1/tenant/{tenant_uuid}"
    saml_sp_config = {
        'debug': settings.DEBUG,
        'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
        'entityid': '%s/metadata/' % baseurl,
        'description':
        'longguikeji SP setup',
        'service': {
            'sp': {
                'name': 'Django SAML2 SP',
                'endpoints': {
                    'assertion_consumer_service': [
                        ('{}/acs/'.format(baseurl), BINDING_HTTP_POST)
                    ],
                    'single_sign_on_service': [
                        ('{}/ls/post'.format(baseurl),BINDING_HTTP_POST),
                        ('{}/ls/redirect'.format(baseurl),BINDING_HTTP_REDIRECT),
                    ],
                },
                'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT],
                'authn_requests_signed': True,
                'want_assertions_signed': True,
                'allow_unsolicited': True,
            },
        },
        'attribute_map_dir': os.path.join(os.path.join(BASE_DIR, 'djangosaml2sp'), 'attribute_maps'),
        'metadata': {
            'local': [
                os.path.join(
                    os.path.join(
                        os.path.join(
                            BASE_DIR, 
                            'djangosaml2sp'
                        ), 
                        'saml2_config'
                    ), 
                    f
                ) for f in os.listdir(
                    BASE_DIR + '/djangosaml2sp/saml2_config/'
                ) if f.split('.')[-1] == 'xml'
            ],
        },
        # Signing
        'key_file': BASE_DIR + f'/djangosaml2sp/certificates/{tenant_uuid}_key.pem',
        'cert_file': BASE_DIR + f'/djangosaml2sp/certificates/{tenant_uuid}_cert.pem',
        # Encryption
        'encryption_keypairs': [{
            'key_file': BASE_DIR + f'/djangosaml2sp/certificates/{tenant_uuid}_key.pem',
            'cert_file': BASE_DIR + f'/djangosaml2sp/certificates/{tenant_uuid}_cert.pem',
        }],
        'valid_for': 365 * 24,
    }
    return saml_sp_config

def saml_sp_config(acs:list,sss:list,key_file:str,crt_file:str):
    