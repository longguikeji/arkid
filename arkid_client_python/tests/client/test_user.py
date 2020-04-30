"""Test For User Client"""
import unittest
import httpretty

from arkid_client.user import UserClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestUserClient(unittest.TestCase):
    """Test For UserClient"""

    client = UserClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_query_user_list(self):
        """测试查询用户列表"""
        register_api_route('user', BASE_URL, '', body=self.list_body)
        response = self.client.query_user_list()
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_query_isolated_user(self):
        """测试查询独立用户"""
        register_api_route('user', BASE_URL, 'isolated/', body=self.list_body)
        response = self.client.query_isolated_user()
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_query_user(self):
        """测试查询指定用户"""
        register_api_route('user', BASE_URL, 'example/', body=self.dict_body)
        response = self.client.query_user(username='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_create_user(self):
        """测试创建用户(需要管理员权限)"""
        register_api_route('user', BASE_URL, '', httpretty.POST, body=self.dict_body)
        response = self.client.create_user(json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_user(self):
        """测试修改指定用户的信息"""
        register_api_route('user', BASE_URL, 'example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_user(username='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_user(self):
        """测试删除指定用户的信息"""
        register_api_route('user', BASE_URL, 'example/', httpretty.DELETE)
        response = self.client.delete_user(username='example')
        self.assertEqual(response.http_status, 200)
