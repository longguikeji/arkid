'''
test tenant switch
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


class TenantSwitchTestCase(TestCase):
    '''
    test tenant switch
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
        url = '/api/v1/tenant_switch/'
        self.client.get(url, content_type='application/json')
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_tenantswitch_get(self):
        '''
        租户开关
        '''
        url = '/api/v1/tenant_switch/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        switch = result.get('switch')
        self.assertTrue(switch)

    def test_tenantswitch_put(self):
        '''
        租户开关
        '''
        url = '/api/v1/tenant_switch/'
        body = {
            'switch': True
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        switch = result.get('switch')
        self.assertTrue(switch)
