'''初始化IdP配置
'''
from __future__ import absolute_import, unicode_literals
from asyncio.log import logger
import copy
import os
from six import text_type
from OpenSSL import crypto
from arkid.config import get_app_config

BASEDIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "certificates/"
)


def create_self_signed_cert(tenant_uuid:str):
    '''
    生成自签名证书存放于相对路径下
    '''
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    cert = crypto.X509()
    cert.get_subject().C = "CN"
    cert.get_subject().CN = get_app_config().get_host()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')
    
    if not os.path.exists(BASEDIR):
        os.mkdir(BASEDIR)

    with open(os.path.join(BASEDIR, f'{tenant_uuid}.crt'), "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(os.path.join(BASEDIR, f'{tenant_uuid}.key'), "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        
def clear_self_signed_cert(tenant_uuid:str):
    """清理自签名文件

    Args:
        tenant_uuid (str): 租户ID
    """
    cert_path = os.path.join(BASEDIR, f'{tenant_uuid}.crt')
    key_path = os.path.join(BASEDIR, f'{tenant_uuid}.key')
    
    if os.path.exists(cert_path):
        os.remove(cert_path)
        
    if os.path.exists(key_path):
        os.remove(key_path)
        
def check_self_signed_cert(tenant_uuid:str):
    """检查自签名文件

    Args:
        tenant_uuid (str): 租户ID
    """
    cert_path = os.path.join(BASEDIR, f'{tenant_uuid}.crt')
    key_path = os.path.join(BASEDIR, f'{tenant_uuid}.key')
    
    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        try:
            os.remove(cert_path)
            os.remove(key_path)
        except Exception as err:
            logger.error(err)
        create_self_signed_cert(tenant_uuid)