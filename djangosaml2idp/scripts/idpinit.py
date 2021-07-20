'''初始化IdP配置
'''
from __future__ import absolute_import, unicode_literals
import copy
import os
from socket import gethostname
from six import text_type
from OpenSSL import crypto
from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor
from djangosaml2idp import idpsettings

BASEDIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


def create_self_signed_cert(tenant_uuid):
    '''
    生成自签名证书存放于相对路径下
    '''
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    cert = crypto.X509()
    cert.get_subject().C = "CN"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    with open(BASEDIR + f'/djangosaml2idp/certificates/{tenant_uuid}_cert.pem', "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(BASEDIR + f"/djangosaml2idp/certificates/{tenant_uuid}_key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


def run(tenant_id, app_id):
    '''配置IdP,生成证书、元数据文件'''
    if not os.path.exists(BASEDIR+f'/djangosaml2idp/certificates/{tenant_id}_cert.pem') or not \
            os.path.exists(BASEDIR+f'/djangosaml2idp/certificates/{tenant_id}_key.pem'):
        create_self_signed_cert(tenant_id)
    if not os.path.exists(BASEDIR + f'/djangosaml2idp/saml2_config/{tenant_id}_{app_id}_idp_metadata.xml'):
        conf = IdPConfig()    # pylint: disable=invalid-name
        conf.load(copy.deepcopy(
            idpsettings.get_saml_idp_config(tenant_id, app_id)))
        meta_data = entity_descriptor(conf)    # pylint: disable=invalid-name
        content = text_type(meta_data).encode('utf-8')
        with open(BASEDIR + f'/djangosaml2idp/saml2_config/{tenant_id}_{app_id}_idp_metadata.xml', 'wb') as f:
            f.write(content)
