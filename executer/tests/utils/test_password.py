'''
test for password_utils
'''

# pylint: disable=missing-docstring

from django.test import TestCase

from executer.utils.password import encrypt_password, verify_password


class PasswordTestCase(TestCase):
    def test_pwd_encrypt_verify(self):
        plaintext = 'password'
        ciphertext = encrypt_password(plaintext, 'MD5')
        self.assertTrue(verify_password(plaintext, ciphertext))

        ciphertext = encrypt_password(plaintext, 'SMD5')
        self.assertTrue(verify_password(plaintext, ciphertext))

        ciphertext = encrypt_password(plaintext, 'SHA')
        self.assertTrue(verify_password(plaintext, ciphertext))

        ciphertext = encrypt_password(plaintext, 'SSHA')
        self.assertTrue(verify_password(plaintext, ciphertext))

        with self.assertRaises(ValueError):
            ciphertext = encrypt_password(plaintext, 'PLAINTEXT')
