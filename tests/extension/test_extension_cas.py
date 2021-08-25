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
from xml.etree import ElementTree

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
            type='cas_server',
        )
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))
        # create extension
        url = '/api/v1/tenant/{}/app/'.format(self.tenant.uuid)
        body = {
            "type": "Cas",
            "data": {

            },
            "name": "cas",
            "url": "http://localhost:8000",
            "description": "cas描述"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        data = result.get('data')
        login = data.get('login')
        validate = data.get('validate')
        self.login_url = login
        self.validate_url = validate
        self.assertIsNotNone(result.get('uuid'))

    def test_extension_userinfo(self):
        # get ticket
        service = 'http://localhost:9528'
        url = '{}?service={}&token={}'.format(
            self.login_url, service, self.token)
        resp = self.client.get(url, content_type='application/json')
        url = resp.url
        self.assertIn(service, url)
        # http://localhost:9528?ticket=ST-1626406570-p0S1tjIWnCFjOPg4dXVkVXArisBdFiSq
        # ticket_index = url.find('ticket=')+7
        # ticket = url[ticket_index:]
        self.ticket = url[url.find('ticket='):]
        # get userinfo
        url = '{}?service={}&{}'.format(self.validate_url, service, self.ticket)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # content = response.content.decode()
        self.assertContains(response, '<cas:id>2</cas:id>')
