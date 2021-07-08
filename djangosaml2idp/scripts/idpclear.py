'''清除IdP配置
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


def run(tenant_id, app_id):
    '''配置IdP,生成证书、元数据文件'''
    idp_metadata_path = BASEDIR + f'/djangosaml2idp/saml2_config/{tenant_id}_{app_id}_idp_metadata.xml'
    if os.path.exists(idp_metadata_path):
        os.remove(idp_metadata_path)

    sp_metadata_path = BASEDIR + f'/djangosaml2idp/saml2_config/{tenant_id}_{app_id}.xml'
    if os.path.exists(sp_metadata_path):
        os.remove(sp_metadata_path)
