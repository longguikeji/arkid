'''
password encryption and verification
'''

from passlib.hash import (
    ldap_md5,
    ldap_sha1,
    ldap_salted_md5,
    ldap_salted_sha1,
)


def encrypt_password(plaintext, encryption):
    '''
    对明文密码进行加密
    加密算法同LDAP，删除了对PLAINTEXT的支持
    :param str plaintext:
    :param str encryption: 加密方式 enum([SSHA, SMD5, MD5, SHA])
    :TODO: To be further about the salt
    '''
    if encryption == 'SSHA':
        return ldap_salted_sha1.hash(plaintext)
    if encryption == 'SMD5':
        return ldap_salted_md5.hash(plaintext)
    if encryption == 'MD5':
        return ldap_md5.hash(plaintext)
    if encryption == 'SHA':
        return ldap_sha1.hash(plaintext)
    if encryption == 'PLAINTEXT':
        raise ValueError("encryption must be one of 'SSHA', 'SMD5', 'SHA', 'MD5'")
    raise ValueError("encryption must be one of 'SSHA', 'SMD5', 'SHA', 'MD5'")


def verify_password(plaintext, ciphertext):
    '''
    对明文密码和密文密码进行校验
    :param str plaintext: 明文密码
    :param str ciphertext: 密文密码
    :return: 密码是否正确
    :rtype: bool
    '''
    if ciphertext.startswith('{SSHA}'):
        return ldap_salted_sha1.verify(plaintext, ciphertext)
    if ciphertext.startswith('{SMD5}'):
        return ldap_salted_md5.verify(plaintext, ciphertext)
    if ciphertext.startswith('{MD5}'):
        return ldap_md5.verify(plaintext, ciphertext)
    if ciphertext.startswith('{SHA}'):
        return ldap_sha1.verify(plaintext, ciphertext)
    return False
