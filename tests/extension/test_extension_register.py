'''
test extension register
'''
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from extension.models import Extension
from inventory.models import User
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from app.models import App

import json

class ExtensionTestCase(TestCase):
    '''
    test extension
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
        # create extension
        self.extension = Extension.objects.create(
            tenant=self.tenant,
            type='oauth2_authorization_server',
        )
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_extension_register(self):
        url = '/api/v1/tenant/{}/extension/{}/'.format(self.tenant.uuid, self.extension.uuid)
        body = {
            'is_active': True,
            'type': 'arkid',
            'data': {}
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        print(result)
