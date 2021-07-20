"""
测试： SSL证书生成与IDP 元数据生成与销毁
"""
import os
from django.test import TestCase
from djangosaml2idp.scripts.idpinit import run as idpinit
from djangosaml2idp.scripts.idpclear import run as idpclear
from djangosaml2idp.scripts.idpinit import BASEDIR


class TestScriptsView(TestCase):
    """
    此处测试SSL证书的生成与清理
    """

    def setUp(self) -> None:
        self.tenant__uuid = "ceshi_tenant__uuid"
        self.app_id = "ceshi_app_id"
        self.key_path = BASEDIR + \
            f'/djangosaml2idp/certificates/{self.tenant__uuid}_key.pem'
        self.cert_path = BASEDIR + \
            f'/djangosaml2idp/certificates/{self.tenant__uuid}_cert.pem'
        self.metadata_path = BASEDIR + \
            f'/djangosaml2idp/saml2_config/{self.tenant__uuid}_{self.app_id}_idp_metadata.xml'
        return super().setUp()

    def test_create_metadata(self):
        """
        测试创建元数据文件
        """
        idpinit(self.tenant__uuid, self.app_id)

        self.assertEqual(os.path.exists(self.key_path), True)
        self.assertEqual(os.path.exists(self.cert_path), True)
        self.assertEqual(os.path.exists(self.metadata_path), True)

    def test_remove_metadata(self):
        """
        测试删除元数据文件
        """
        idpclear(self.tenant__uuid, self.app_id)
        self.assertEqual(os.path.exists(self.metadata_path), False)
