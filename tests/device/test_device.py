'''
test device
'''
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant, TenantDevice
from inventory.models import User
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

import json


class DeviceTestCase(TestCase):
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
        # create device
        self.device = TenantDevice.objects.create(
            tenant=self.tenant,
            device_type='pc',
            system_version='mac 10.11',
            browser_version='chrome 3.0.11',
            ip='127.0.0.1',
            mac_address='12:13:14:15',
            device_number='sdasdas',
            device_id='12345678',
            account_ids=['123456','7890']
        )
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_device_create(self):
        url = '/api/v1/tenant/{}/device/'.format(self.tenant.uuid)
        body = {
            "device_type": "手机",
            "system_version": "mac 10.11",
            "browser_version": "chrome 3.0",
            "ip": "127.0.0.1",
            "mac_address": "12:12:33:44:22",
            "device_number": "83621321",
            "device_id": "123",
            "account_ids": ["12321321", "12321321"]
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
    
    def test_device_list(self):
        url = '/api/v1/tenant/{}/device/'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        count = result.get('count')
        self.assertIsNotNone(count)
    
    def test_device_export(self):
        url = '/api/v1/tenant/{}/device_export/'.format(self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_device_delete(self):
        url = '/api/v1/tenant/{}/device/{}/detail/'.format(self.tenant.uuid, self.device.uuid)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())
