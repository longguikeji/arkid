"""Test For Perm Client"""

import unittest
import httpretty

from arkid_client.perm import PermClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestPermClient(unittest.TestCase):
    """Test For PermClient"""

    client = PermClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_query_all_perm(self):
        """测试获取所有权限"""
        register_api_route('perm', BASE_URL, '', body=self.list_body)
        response = self.client.query_all_perm()
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_create_perm(self):
        """测试创建权限"""
        register_api_route('perm', BASE_URL, '', httpretty.POST, body=self.dict_body)
        response = self.client.create_perm(json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_perm(self):
        """测试查询指定权限"""
        register_api_route('perm', BASE_URL, 'example/', body=self.dict_body)
        response = self.client.query_perm(uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_perm(self):
        """测试更新指定权限"""
        register_api_route('perm', BASE_URL, 'example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_perm(uid='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_perm_owner(self):
        """测试获取某权限指定类型的所有者"""
        register_api_route('perm', BASE_URL, 'example/owner/', body=self.dict_body)
        response = self.client.query_perm_owner(uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_perm_owner(self):
        """测试获取某权限指定类型的所有者"""
        register_api_route('perm', BASE_URL, 'example/owner/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_perm_owner(uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_specified_user_perm(self):
        """测试获取用户所有权限"""
        register_api_route('perm', BASE_URL, 'user/example/', body=self.list_body)
        response = self.client.query_specified_user_perm('example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def update_specified_user_perm(self):
        """测试更新用户所有权限"""
        register_api_route('perm', BASE_URL, 'user/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_specified_user_perm('example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_dept_perm(self):
        """测试获取部门所有权限"""
        register_api_route('perm', BASE_URL, 'dept/example/', body=self.list_body)
        response = self.client.query_dept_perm('example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_update_dept_perm(self):
        """测试更新部门权限"""
        register_api_route('perm', BASE_URL, 'dept/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_dept_perm('example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_group_perm(self):
        """测试获取组所有权限"""
        register_api_route('perm', BASE_URL, 'group/example/', body=self.list_body)
        response = self.client.query_group_perm('example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_update_group_perm(self):
        """测试获更新组权限"""
        register_api_route('perm', BASE_URL, 'group/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_group_perm('example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_node_perm(self):
        """测试获取节点所有权限"""
        register_api_route('perm', BASE_URL, 'node/example/', body=self.list_body)
        response = self.client.query_node_perm('example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_update_node_perm(self):
        """测试更新节点所有权限"""
        register_api_route('perm', BASE_URL, 'node/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_node_perm('example', json_body={})
        self.assertEqual(response.text, self.dict_body)
