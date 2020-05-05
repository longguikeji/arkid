"""Test For Ucenter Client"""

import unittest
import httpretty

from arkid_client.ucenter import UcenterClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestUcenterClient(unittest.TestCase):
    """Test For UcenterClient"""

    client = UcenterClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_view_perm(self):
        """测试获取用户权限"""
        register_api_route('ucenter', BASE_URL, 'perm/', body=self.list_body)
        response = self.client.view_perm()
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_view_profile(self):
        """测试获取用户自身信息"""
        register_api_route('ucenter', BASE_URL, 'profile/', body=self.dict_body)
        response = self.client.view_profile()
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_view_current_org(self):
        """测试获取用户当前所在组织的信息"""
        register_api_route('ucenter', BASE_URL, 'org/', body=self.dict_body)
        response = self.client.view_current_org()
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_switch_current_org(self):
        """测试切换用户当前所在的组织"""
        register_api_route('ucenter', BASE_URL, 'org/', httpretty.PUT, body=self.dict_body)
        response = self.client.switch_current_org(json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_apps(self):
        """测试普通用户获取可见应用列表"""
        register_api_route('ucenter', BASE_URL, 'apps/', body=self.list_body)
        response = self.client.query_apps()
        self.assertEqual(response.text, self.list_body)
