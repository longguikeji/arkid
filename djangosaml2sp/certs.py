"""
自签名工具
"""
import os
from socket import gethostname
from OpenSSL import crypto
from djangosaml2sp.spsettings import BASE_DIR


def create_self_signed_cert(tenant_uuid):
    '''
    生成自签名证书存放于相对路径下
    '''
    cert_file_path = BASE_DIR + \
        f'/djangosaml2sp/certificates/{tenant_uuid}_cert.pem'
    key_file_path = BASE_DIR + \
        f"/djangosaml2sp/certificates/{tenant_uuid}_key.pem"
    if not os.path.exists(cert_file_path) or not os.path.exists(key_file_path):
        clear_self_signed_cert(tenant_uuid)

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

        with open(cert_file_path, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_file_path, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


def clear_self_signed_cert(tenant_uuid):
    """
    清理自签名文件
    """
    file_name_prefix = f"{BASE_DIR}/djangosaml2sp/certificates/{tenant_uuid}"
    if os.path.exists(f"{file_name_prefix}_cert.pem"):
        os.remove(f"{file_name_prefix}_cert.pem")

    if os.path.exists(f"{file_name_prefix}_key.pem"):
        os.remove(f"{file_name_prefix}_key.pem")
