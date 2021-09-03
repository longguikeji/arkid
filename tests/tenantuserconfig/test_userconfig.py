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

    def test_tenant_userconfig(self):
        url = '/api/v1/tenant/{}/userconfig'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        is_logout = result.get('is_logout')
        self.assertFalse(is_logout)

    def test_tenant_userfields(self):
        url = '/api/v1/tenant/{}/userfields'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        fields = result.get('fields')
        self.assertIn('mobile', fields)