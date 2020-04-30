"""Test For ArkID Client"""
import unittest
import httpretty

from arkid_client.client import ArkIDClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestArkIDClient(unittest.TestCase):
    """Test For ArkIDClient"""

    client = ArkIDClient(base_url=BASE_URL, authorizer=basic_authorizer())
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

    @httpretty.activate
    def test_query_own_org(self):
        """测试查询用户所在的组织"""
        register_api_route('org', BASE_URL, '', body=self.list_body)
        response = self.client.query_own_org()
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_query_org(self):
        """测试查看指定组织的信息"""
        register_api_route('org', BASE_URL, 'example/', body=self.dict_body)
        response = self.client.query_org(oid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_create_org(self):
        """测试创建组织"""
        register_api_route('org', BASE_URL, '', httpretty.POST, body=self.dict_body)
        response = self.client.create_org(json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_org(self):
        """测试删除指定组织的信息"""
        register_api_route('org', BASE_URL, 'example/', httpretty.DELETE)
        response = self.client.delete_org(oid='example')
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_update_org(self):
        """测试修改指定组织的信息"""
        register_api_route('org', BASE_URL, 'example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_org(oid='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_orguser_list(self):
        """测试查看特定组织的成员信息"""
        register_api_route('org', BASE_URL, 'example/user/', body=self.list_body)
        response = self.client.query_orguser_list(oid='example')
        self.assertEqual(response.text, self.list_body)

    @httpretty.activate
    def test_add_orguser(self):
        """测试向指定组织中添加成员"""
        register_api_route('org', BASE_URL, 'example/user/', httpretty.PATCH, body=self.dict_body)
        response = self.client.add_orguser(oid='example', usernames=[])
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_orguser(self):
        """测试从指定组织中移除成员"""
        register_api_route('org', BASE_URL, 'example/user/', httpretty.PATCH)
        response = self.client.delete_orguser(oid='example', usernames=[])
        self.assertEqual(response.http_status, 200)

    @httpretty.activate
    def test_query_orguser(self):
        """测试查看指定组织的指定成员的信息"""
        register_api_route('org', BASE_URL, 'example/user/example/', body=self.dict_body)
        response = self.client.query_orguser(oid='example', username='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_orguser(self):
        """测试编辑指定组织的指定成员的信息"""
        register_api_route('org', BASE_URL, 'example/user/example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_orguser(oid='example', username='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_get_org_invitation_key(self):
        """测试获取指定组织邀请用的最新的密钥"""
        register_api_route('org', BASE_URL, 'example/invitation/', body=self.dict_body)
        response = self.client.get_org_invitation_key(oid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_refresh_org_invitation_key(self):
        """测试获取指定组织邀请用的最新的密钥"""
        register_api_route('org', BASE_URL, 'example/invitation/', httpretty.PUT, body=self.dict_body)
        response = self.client.refresh_org_invitation_key(oid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_view_org_by_invitation_key(self):
        """测试使用邀请密钥查看指定组织的信息"""
        register_api_route('org', BASE_URL, 'example/invitation/example/', body=self.dict_body)
        response = self.client.view_org_by_invitation_key(oid='example', invite_link_key='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_join_org_by_invitation_key(self):
        """测试使用邀请密钥加入指定组织"""
        register_api_route('org', BASE_URL, 'example/invitation/example/', httpretty.POST, body=self.dict_body)
        response = self.client.join_org_by_invitation_key(oid='example', invite_link_key='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_get_current_org(self):
        """测试获取用户当前所在组织的信息"""
        register_api_route('ucenter', BASE_URL, 'org/', body=self.dict_body)
        response = self.client.get_current_org()
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_switch_current_org(self):
        """测试切换用户当前所在的组织"""
        register_api_route('ucenter', BASE_URL, 'org/', httpretty.PUT, body=self.dict_body)
        response = self.client.switch_current_org(json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_query_node(self):
        """测试查询指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', body=self.dict_body)
        response = self.client.query_node(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_view_node(self):
        """测试用户查询指定节点的信息"""
        register_api_route('ucenter', BASE_URL, 'node/example/', body=self.dict_body)
        response = self.client.view_node(node_uid='example')
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_update_node(self):
        """测试修改指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', httpretty.PATCH, body=self.dict_body)
        response = self.client.update_node(node_uid='example', json_body={})
        self.assertEqual(response.text, self.dict_body)

    @httpretty.activate
    def test_delete_node(self):
        """测试删除指定节点的信息"""
        register_api_route('node', BASE_URL, 'example/', httpretty.DELETE)
        response = self.client.delete_node(node_uid='example')
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
