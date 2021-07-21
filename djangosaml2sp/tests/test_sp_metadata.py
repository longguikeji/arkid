"""
SAML2.0 SP 测试metadata接口
"""
import os
import uuid
from django.http import HttpRequest
from django.test import TestCase
from djangosaml2sp.views import metadata, download_metadata
from djangosaml2sp.certs import create_self_signed_cert, clear_self_signed_cert
from djangosaml2sp.spsettings import BASE_DIR


class TestMetadataView(TestCase):
    """
    测试错误页面接口
    """

    def setUp(self) -> None:
        self.tenant_uuid = uuid.uuid4()
        return super().setUp()

    def test_cert(self):
        """
        测试自签名证书
        """
        create_self_signed_cert(self.tenant_uuid)
        file_name_prefix = f"{BASE_DIR}/djangosaml2sp/certificates/{self.tenant_uuid}"
        self.assertEqual(os.path.exists(f"{file_name_prefix}_cert.pem"), True)
        self.assertEqual(os.path.exists(f"{file_name_prefix}_key.pem"), True)
        clear_self_signed_cert(self.tenant_uuid)
        self.assertEqual(os.path.exists(f"{file_name_prefix}_cert.pem"), False)
        self.assertEqual(os.path.exists(f"{file_name_prefix}_key.pem"), False)

    def test_metadata(self):
        """
        测试获取元数据文件
        """
        create_self_signed_cert(self.tenant_uuid)
        request = HttpRequest()
        request.method = 'GET'
        response = metadata(request, self.tenant_uuid)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/xml; charset=utf8"
        clear_self_signed_cert(self.tenant_uuid)

    def test_download_metadata(self):
        """
        测试下载元数据文件
        """
        create_self_signed_cert(self.tenant_uuid)
        request = HttpRequest()
        request.method = 'GET'
        response = download_metadata(request, self.tenant_uuid)
        assert response.status_code == 200
        assert response.headers["content-type"] == 'application/octet-stream'
        clear_self_signed_cert(self.tenant_uuid)
