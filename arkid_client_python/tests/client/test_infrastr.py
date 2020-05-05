"""Test For Infrastructure Client"""

import unittest
import httpretty

from arkid_client.infrastructure import InfrastructureClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestInfrastructureClient(unittest.TestCase):
    """Test For InfrastructureClient"""

    client = InfrastructureClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_get_sms_captcha(self):
        """测试获取短信验证码"""
        actions_map = {
            'register': 'sms/register/',
            'login': 'sms/login/',
            'reset_password': 'sms/reset_password/',
            'activate_user': 'sms/activate_user/',
            'update_mobile': 'sms/update_mobile/',
            'general': 'sms/',
        }
        for key, value in actions_map.items():
            register_api_route('infrastructure', BASE_URL, value, httpretty.POST)
            response = self.client.get_sms_captcha(key, 'example')
            self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_verify_sms_captcha(self):
        """测试验证短信验证码"""
        actions_map = {
            'register': 'sms/register/',
            'login': 'sms/login/',
            'reset_password': 'sms/reset_password/',
            'activate_user': 'sms/activate_user/',
            'update_mobile': 'sms/update_mobile/',
            'general': 'sms/',
        }
        for key, value in actions_map.items():
            register_api_route('infrastructure', BASE_URL, value)
            response = self.client.verify_sms_captcha(key, 'example', 'example')
            self.assertEqual(response.http_status, 200)
