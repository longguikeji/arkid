'''
test device
'''
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from inventory.models import User, Permission, PermissionGroup, Group
from django.contrib.contenttypes.models import ContentType
from extension.models import Extension
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from app.models import App

import json


class UserConfigTestCase(TestCase):
    '''
    test device
    '''

    def setUp(self):
        # create tenant
        self.tenant = Tenant.objects.create(name='first tenant')
        # create user
        self.user = User.objects.create(
            first_name='Super',
            last_name='Admin',
            username='superuser',
            password=make_password('password1'),
        )
        self.app = App.objects.create(
            tenant=self.tenant,
            name="test_app",
            url="http://www.test.com",
            logo="",
            description="用于测试的app",
            type="oAuth",
            data={},
            auth_tmpl=''
        )
        self.token = self.user.token
        self.permission = Permission.objects.create(
            name="权限1",
            content_type=ContentType.objects.get_for_model(App),
            codename="custome_ssdada",
            tenant=self.tenant,
            app=self.app,
            permission_category="入口",
            is_system_permission=False,
        )
        self.permission_group=PermissionGroup.objects.create(
            name="权限组1",
            is_system_group=False,
            tenant=self.tenant,
        )
        self.group=Group.objects.create(
            tenant=self.tenant,
            name='分组1',
            parent=None,
        )
        self.permission_group.permissions.add(self.permission)
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_permission_list(self):
        '''
        权限列表
        '''
        url = '/api/v1/tenant/{}/permission/'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        results = result.get('results')
        self.assertIsNotNone(results)

    def test_permission_create(self):
        '''
        创建权限
        '''
        url = '/api/v1/tenant/{}/permission/create'.format(self.tenant.uuid)
        body = {
            "name": "测试权限创建",
            "app_uuid": self.app.uuid_hex,
            "permission_category": "入口"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
    
    def test_permission_edit(self):
        '''
        编辑权限
        '''
        url = '/api/v1/tenant/{}/permission/{}/detail'.format(self.tenant.uuid, self.permission.uuid)
        body = {
            "name": "测试权限创建2",
            "app_uuid": self.app.uuid_hex,
            "permission_category": "入口"
        }
        resp = self.client.put(url, body, content_type='application/json')
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
    
    def test_permission_delete(self):
        '''
        删除权限
        '''
        url = '/api/v1/tenant/{}/permission/{}/detail'.format(self.tenant.uuid, self.permission.uuid)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())
    
    def test_permission_group(self):
        '''
        权限组列表
        '''
        url = '/api/v1/tenant/{}/permission_group/'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        results = result.get('results')
        self.assertIsNotNone(results)

    def test_permission_group_create(self):
        '''
        创建权限组
        '''
        url = '/api/v1/tenant/{}/permission_group/create'.format(self.tenant.uuid)
        body = {
            "name": "权限组2",
            "permissions": [self.permission.uuid_hex]
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
    
    def test_permission_group_edit(self):
        '''
        编辑权限
        '''
        url = '/api/v1/tenant/{}/permission_group/{}/detail'.format(self.tenant.uuid_hex, self.permission_group.uuid_hex)
        body = {
            "name": "权限组3",
            "permissions": [self.permission.uuid_hex]
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
    
    def test_permission_group_delete(self):
        '''
        删除权限组
        '''
        url = '/api/v1/tenant/{}/permission_group/{}/detail'.format(self.tenant.uuid_hex, self.permission_group.uuid_hex)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())

    def test_user_permission_list(self):
        '''
        用户权限列表
        '''
        url = '/api/v1/tenant/{}/user_permission/{}/'.format(self.tenant.uuid_hex, self.user.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_permission_create(self):
        '''
        用户权限创建
        '''
        url = '/api/v1/tenant/{}/user_permission/{}/create'.format(self.tenant.uuid_hex, self.user.uuid_hex)
        body = {
            "permissions": [self.permission.uuid_hex]
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
    
    def test_user_permission_delete(self):
        '''
        删除用户权限
        '''
        url = '/api/v1/tenant/{}/user_permission/{}/delete/'.format(self.tenant.uuid_hex, self.user.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_group_permission_list(self):
        '''
        分组权限列表
        '''
        url = '/api/v1/tenant/{}/group_permission/{}/'.format(self.tenant.uuid_hex, self.group.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_group_permission_create(self):
        '''
        分组权限创建
        '''
        url = '/api/v1/tenant/{}/group_permission/{}/create'.format(self.tenant.uuid_hex, self.group.uuid_hex)
        body = {
            "permissions": [self.permission.uuid_hex]
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
    
    def test_group_permission_delete(self):
        '''
        删除分组权限
        '''
        url = '/api/v1/tenant/{}/group_permission/{}/delete/'.format(self.tenant.uuid_hex, self.group.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_app_permission(self):
        '''
        app权限列表
        '''
        url = '/api/v1/tenant/{}/app_permission/{}/'.format(self.tenant.uuid_hex, self.app.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
