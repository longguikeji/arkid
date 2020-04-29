"""Test For Node Client"""

import unittest
import httpretty

from arkid_client.node import NodeClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestNodeClient(unittest.TestCase):
    """Test For NodeClient"""

    client = NodeClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

    @httpretty.activate
    def test_query_specified_node(self):
        """测试查询指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', body=self.dict_body)
        response = self.client.query_specified_node(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_view_specified_node(self):
        """测试用户查询指定节点的信息"""
        register_api_route('ucenter', BASE_URL, 'node/example/', body=self.dict_body)
        response = self.client.view_specified_node(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_specified_node(self):
        """测试修改指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_specified_node(node_uid='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_specified_node(self):
        """测试删除指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', httpretty.DELETE)
        response = self.client.delete_specified_node(node_uid='example')
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_get_node_tree(self):
        """测试获取指定节点下的完整树结构"""
        register_api_route('node', BASE_URL, 'example/tree/', body=self.dict_body)
        response = self.client.get_node_tree(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_view_node_tree(self):
        """测试用户查看指定节点下的树结构"""
        register_api_route('ucenter', BASE_URL, 'node/example/tree/', body=self.dict_body)
        response = self.client.view_node_tree(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_get_subnode(self):
        """测试获取指定节点的子节点信息"""
        register_api_route('node', BASE_URL, 'example/node/', body=self.dict_body)
        response = self.client.get_subnode(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_create_subnode(self):
        """测试创建指定节点的子节点"""
        register_api_route('node', BASE_URL, 'example/node/', httpretty.POST, body=self.dict_body)
        response = self.client.create_subnode(node_uid='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_add_subnode(self):
        """测试向指定节点添加子节点"""
        register_api_route('node', BASE_URL, 'example/node/', httpretty.PATCH, body=self.dict_body)
        response = self.client.add_subnode(node_uid='example', node_uids=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_sort_subnode(self):
        """测试对指定子节点按指定位置进行排序"""
        register_api_route('node', BASE_URL, 'example/node/', httpretty.PATCH, body=self.dict_body)
        response = self.client.sort_subnode(node_uid='example', node_uids=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_user_under_node(self):
        """测试查询指定节点下的直属人员的信息"""
        register_api_route('node', BASE_URL, 'example/user/', body=self.list_body)
        response = self.client.query_user_under_node(node_uid='example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_add_user_under_node(self):
        """测试向指定节点添加指定成员"""
        register_api_route('node', BASE_URL, 'example/user/', httpretty.PATCH, body=self.dict_body)
        response = self.client.add_user_under_node(node_uid='example', user_uids=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_user_under_node(self):
        """测试从指定节点移除指定成员"""
        register_api_route('node', BASE_URL, 'example/user/', httpretty.PATCH)
        response = self.client.delete_user_under_node(node_uid='example', user_uids=[])
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_override_user_under_node(self):
        """测试重置指定节点的指定用户"""
        register_api_route('node', BASE_URL, 'example/user/', httpretty.PATCH, body=self.dict_body)
        response = self.client.override_user_under_node(node_uid='example', user_uids=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_sort_user_under_node(self):
        """测试对指定人按指定位置进行排序"""
        register_api_route('node', BASE_URL, 'example/user/', httpretty.PATCH, body=self.dict_body)
        response = self.client.sort_user_under_node(node_uid='example', user_uids=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_move_out_user_under_node(self):
        """测试将成员从指定节点移除，并加到指定节点"""
        register_api_route('node', BASE_URL, 'example/user/', httpretty.PATCH, body=self.dict_body)
        response = self.client.move_out_user_under_node(node_uid='example', user_uids=[])
        self.assertEqual(response.text, self.dict_body)
