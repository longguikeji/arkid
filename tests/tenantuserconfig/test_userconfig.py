'''
test device
'''
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from device.models import Device
from inventory.models import User
from extension.models import Extension
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

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
        self.token = self.user.token
        # 注册插件
        self.extension = Extension.objects.create(
            tenant=self.tenant,
            type='tenantuserconfig',
        )
        url = '/api/v1/tenant/{}/extension/{}/'.format(
            self.tenant.uuid, self.extension.uuid)
        body = {
            'is_active': True,
            'type': 'tenantuserconfig',
            'data': {}
        }
        self.client.put(url, body, content_type='application/json')
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_tenant_editfields(self):
        '''
        租户编辑字段列表(不没选择的)
        '''
        url = '/api/v1/tenant/{}/userconfig/editfields'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        results = result.get('results')
        self.assertIn({'name': '昵称', 'en_name': 'nickname', 'type': 'string'}, results)

    def test_tenant_logout(self):
        '''
        租户登出设置
        '''
        url = '/api/v1/tenant/{}/userconfig/logout'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        is_logout = result.get('is_logout')
        self.assertFalse(is_logout)
    
    def test_tenant_logging(self):
        '''
        租户记录设置
        '''
        url = '/api/v1/tenant/{}/userconfig/logging'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        is_logging_ip = result.get('is_logging_ip')
        is_logging_device = result.get('is_logging_device')
        self.assertTrue(is_logging_ip)
        self.assertTrue(is_logging_device)

    def test_tenant_token(self):
        '''
        租户token设置
        '''
        url = '/api/v1/tenant/{}/userconfig/token'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        is_look_token = result.get('is_look_token')
        is_manual_overdue_token = result.get('is_manual_overdue_token')
        self.assertFalse(is_look_token)
        self.assertFalse(is_manual_overdue_token)

    def test_tenant_editfield(self):
        '''
        租户编辑字段列表(含没选择的)
        '''
        url = '/api/v1/tenant/{}/userconfig/editfield'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        results = result.get('results')
        self.assertIn({'name': '昵称', 'en_name': 'nickname', 'type': 'string', 'is_select': True}, results)
