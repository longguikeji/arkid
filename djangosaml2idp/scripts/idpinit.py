'''初始化IdP配置
'''
from __future__ import absolute_import, unicode_literals
import copy
import os
from six import text_type
from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor
from djangosaml2idp import idpsettings
from djangosaml2idp.idpview import create_self_signed_cert

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run():
    '''配置IdP,生成证书、元数据文件'''
    if not os.path.exists(BASEDIR+'/djangosaml2idp/certificates/mycert.pem') or not \
        os.path.exists(BASEDIR+'/djangosaml2idp/certificates/mykey.pem'):
        create_self_signed_cert()

    conf = IdPConfig()    # pylint: disable=invalid-name
    conf.load(copy.deepcopy(idpsettings.SAML_IDP_CONFIG))
    meta_data = entity_descriptor(conf)    # pylint: disable=invalid-name
    content = text_type(meta_data).encode('utf-8')
    with open(BASEDIR + '/djangosaml2idp/saml2_config/idp_metadata.xml', 'wb') as f:
        f.write(content)
