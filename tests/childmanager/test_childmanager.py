'''
test childmanager
'''
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from device.models import Device
from inventory.models import User
from extension.models import Extension
from extension_root.childmanager.models import ChildManager
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

import json


class ChildAccountTestCase(TestCase):
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
        self.token = self.user.token
        # 注册插件
        self.extension = Extension.objects.create(
            tenant=self.tenant,
            type='childmanager',
        )
        self.childmanager = ChildManager.objects.create(
            tenant=self.tenant,
            user=self.user,
            data={
                "manager_visible": ["所在分组","指定分组与账号"],
                "manager_permission": "全部权限",
                "assign_group": [],
                "assign_user": [],
                "assign_permission": []
            }
        )
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_childmanager(self):
        '''
        子管理员列表
        '''
        url = '/api/v1/tenant/{}/childmanager/'.format(self.tenant.uuid_hex)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        count = result.get('count')
        self.assertIs(1, count)

    def test_childmanager_create(self):
        '''
        创建子管理员
        '''
        url = '/api/v1/tenant/{}/childmanager/create'.format(self.tenant.uuid_hex)
        body = {
            "user_uuid": self.user.uuid_hex,
            "data": {
                "manager_visible": [
                "所在分组"
                ],
                "manager_permission": "全部权限",
                "assign_group": [],
                "assign_user": [],
                "assign_permission": []
            }
        }
        resp = self.client.post(url, body, content_type='application/json')
        result = json.loads(resp.content.decode())
        user_uuid = result.get('user_uuid')
        self.assertEqual(str(self.user.uuid), user_uuid)

    def test_childmanager_edit(self):
        '''
        编辑子管理员
        '''
        url = '/api/v1/tenant/{}/childmanager/{}/detail/'.format(self.tenant.uuid_hex, self.childmanager.uuid_hex)
        body = {
            "user_uuid": self.user.uuid_hex,
            "data": {
                "manager_visible": [
                "所在分组的下级分组"
                ],
                "manager_permission": "全部权限",
                "assign_group": [],
                "assign_user": [],
                "assign_permission": []
            }
        }
        resp = self.client.put(url, body, content_type='application/json')
        result = json.loads(resp.content.decode())
        user_uuid = result.get('user_uuid')
        self.assertEqual(str(self.user.uuid), user_uuid)

    def test_childmanager_delete(self):
        '''
        删除子管理员
        '''
        url = '/api/v1/tenant/{}/childmanager/{}/detail/'.format(self.tenant.uuid_hex, self.childmanager.uuid_hex)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())
