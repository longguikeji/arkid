"""
测试错误页面接口
"""
from django.http import HttpRequest
from django.test import TestCase
from djangosaml2idp.views import SAML2IDPError

class TestErrorView(TestCase):
    """
    测试错误页面接口
    """
    def test_uses_correct_template(self):
        """
        正确获取错误页面
        """
        request = HttpRequest()
        request.method = 'GET'
        response = SAML2IDPError.as_view()(request)
        assert response.status_code == 200
