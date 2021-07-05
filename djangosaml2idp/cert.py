import os
from OpenSSL import crypto
from socket import gethostname
    
def create_self_signed_cert(base_dir):
    """
    创建自签名证书
    """
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

    with open(base_dir + 'cert.pem', "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(base_dir + "key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

def check_or_create_self_signed_cert(base_dir):
    """
    检查目录下是否存在SSL证书，如无则创建
    """

    if not os.path.exists(os.path.join(base_dir,"cert.pem")) or not \
        os.path.exists(os.path.join(base_dir,"key.pem")):

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        create_self_signed_cert(base_dir)