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
            type='childaccount',
        )
        url = '/api/v1/tenant/{}/extension/{}/'.format(
            self.tenant.uuid, self.extension.uuid)
        body = {
            'is_active': True,
            'type': 'childaccount',
            'data': {}
        }
        self.client.put(url, body, content_type='application/json')
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_childaccount(self):
        url = '/api/v1/childaccounts/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        count = result.get('count')
        self.assertIs(1, count)

    def test_childaccount_create(self):
        url = '/api/v1/childaccounts/'
        body = {
            'username': 'zzz',
            'password': 'adminadmin1',
            'mobile': '15291584677',
            'email': '15291584677@qq.com'
        }
        resp = self.client.post(url, body, content_type='application/json')
        result = json.loads(resp.content.decode())
        username = result.get('username')
        self.assertEqual('zzz', username)
