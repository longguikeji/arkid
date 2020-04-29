"""Test For Auth Client"""

import unittest
import httpretty

from arkid_client.auth import ConfidentialAppAuthClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestConfidentialAppAuthClient(unittest.TestCase):
    """Test For ConfidentialAppAuthClient"""

    login_body = "{'token': 'ONEID_TOKEN', 'expires_in': 1234}"
    client = ConfidentialAppAuthClient(base_url=BASE_URL)

    @httpretty.activate
    def test_auth_to_get_token(self):
        """测试身份认证"""
        register_api_route('ucenter', BASE_URL, 'login/', httpretty.POST, body=self.login_body)
        response = self.client.start_auth('example', 'example')
        self.assertEqual(response.text, self.login_body)

    @httpretty.activate
    def test_revoke_token(self):
        """测试撤销 ``oneid_token``"""
        register_api_route('revoke', BASE_URL, 'token/', httpretty.POST)
        response = self.client.revoke_token(basic_authorizer())
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_auth_token(self):
        """测试校验 ``oneid_token`` 所代表的用户是否有某特定权限"""
        register_api_route('auth', BASE_URL, 'token/')
        response = self.client.auth_token(basic_authorizer())
        self.assertEqual(response.http_status, 200)
