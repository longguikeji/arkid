"""Test For App Client"""

import unittest
import httpretty

from arkid_client.app import AppClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestAppClient(unittest.TestCase):
    """Test For AppClient"""

    client = AppClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_query_app_list(self):
        """测试获取应用信息列表"""
        register_api_route('org', BASE_URL, 'example/app', body=self.list_body)
        response = self.client.query_app_list('example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_create_app(self):
        """测试创建应用"""
        register_api_route('org', BASE_URL, 'example/app', httpretty.POST, body=self.dict_body)
        response = self.client.create_app('example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_app(self):
        """测试获取特定应用"""
        register_api_route('org', BASE_URL, 'example/app/example/', body=self.dict_body)
        response = self.client.query_app('example', 'example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_app(self):
        """测试更新特定应用"""
        register_api_route('org', BASE_URL, 'example/app/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_app('example', 'example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_app(self):
        """测试删除特定应用"""
        register_api_route('org', BASE_URL, 'example/app/example/', httpretty.DELETE)
        response = self.client.delete_app('example', 'example')
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_register_app(self):
        """测试注册应用"""
        protocols_map = {
            'oauth': 'oauth/',
        }
        for key, value in protocols_map.items():
            register_api_route('org', BASE_URL, 'example/app/example/{}/'.format(value), httpretty.POST, body=self.dict_body)
            response = self.client.register_app('example', 'example', key, json_body={})
            self.assertEqual(response.text, self.dict_body)
