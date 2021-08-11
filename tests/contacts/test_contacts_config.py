'''
test contacts config
'''
from unittest import mock
from django.test import TestCase

from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from inventory.models import User
from xml.etree import ElementTree
from tenant.models import Tenant, TenantContactsConfig, TenantContactsUserFieldConfig

import json


class ContactsConfigCase(TestCase):
    '''
    contacts config
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
        TenantContactsConfig.objects.get_or_create(
            is_del=False,
            tenant=self.tenant,
            config_type=0,
            data={
                "is_open": True
            }
        )
        TenantContactsConfig.objects.get_or_create(
            is_del=False,
            tenant=self.tenant,
            config_type=1,
            data={
                "visible_type": '所有人可见',
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        tcufc, created = TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=self.tenant,
                name="用户名",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
        )
        self.tcufc = tcufc
        self.token = self.user.token
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.service = 'http://localhost:8000'

    def test_function_switch(self):
        url = '{}/api/v1/tenant/{}/contactsconfig/function_switch/'.format(self.service, self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content.decode())
        is_open = content.get('data').get('is_open')
        self.assertTrue(is_open)

    def test_group_visibility(self):
        url = '{}/api/v1/tenant/{}/contactsconfig/group_visibility/'.format(self.service, self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content.decode())
        visible_type = content.get('data').get('visible_type')
        self.assertEqual(visible_type, '所有人可见')
    
    def test_info_visibility(self):
        url = '{}/api/v1/tenant/{}/contactsconfig/info_visibility/'.format(self.service, self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content.decode())
        results = content.get('results')
        for item in results:
            visible_type = item.get('data').get('visible_type')
            name = item.get('name')
            self.assertEqual(visible_type, '所有人可见')
            self.assertEqual(name, '用户名')
    
    def test_info_visibility_detail(self):
        url = '{}/api/v1/tenant/{}/contactsconfig/info_visibility/{}/detail/'.format(self.service, self.tenant.uuid, self.tcufc.uuid)
        body = {
            'data': {
                'visible_type': '部分人可见',
                'visible_scope': ['本人可见'],
                'assign_group': [],
                'assign_user': []
            }
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content.decode())
        visible_type = content.get('data').get('visible_type')
        visible_scope = content.get('data').get('visible_scope')
        self.assertEqual(visible_type, '部分人可见')
        self.assertEqual(visible_scope, ['本人可见'])
