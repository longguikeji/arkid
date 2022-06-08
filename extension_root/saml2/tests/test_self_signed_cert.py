"""
测试： SSL证书生成与IDP 元数据生成与销毁
"""
import os
from django.test import TestCase
from ..common.certs import BASEDIR,create_self_signed_cert,clear_self_signed_cert

class TestSelfSignedCertView(TestCase):
    """
    此处测试SSL证书的生成与清理
    """

    def setUp(self) -> None:
        self.tenant__uuid = "ceshi_tenant__uuid"
        self.key_path = os.path.join(BASEDIR, f'{self.tenant__uuid}.key')
        self.cert_path = os.path.join(BASEDIR, f'{self.tenant__uuid}.crt')
        return super().setUp()

    def test_create_metadata(self):
        """
        测试创建元数据文件
        """
        create_self_signed_cert(self.tenant__uuid)

        self.assertEqual(os.path.exists(self.key_path), True)
        self.assertEqual(os.path.exists(self.cert_path), True)

    def test_remove_metadata(self):
        """
        测试删除元数据文件
        """
        clear_self_signed_cert(self.tenant__uuid)
        self.assertEqual(os.path.exists(self.key_path), False)
        self.assertEqual(os.path.exists(self.cert_path), False)