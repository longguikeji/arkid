"""Test For Org Client"""

import unittest
import httpretty

from arkid_client.org import OrgClient
from arkid_client.authorizers import BasicAuthorizer
from tests.common import register_api_route

BASE_URL = 'https://arkid.longguikeji.com/'


def basic_authorizer():
    """提供默认的授权器"""
    return BasicAuthorizer(oneid_token='test token')


class TestOrgClient(unittest.TestCase):
    """Test For OrgClient"""

    client = OrgClient(base_url=BASE_URL, authorizer=basic_authorizer())
    dict_body = '{}'
    list_body = '[]'

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
