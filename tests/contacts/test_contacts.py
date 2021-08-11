'''
test contacts config
'''
from unittest import mock
from django.test import TestCase

from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from inventory.models import User, Group
from xml.etree import ElementTree
from tenant.models import Tenant, TenantContactsConfig, TenantContactsUserFieldConfig

import json


class ContactsCase(TestCase):
    '''
    contacts
    '''

    def setUp(self):
        # create tenant
        self.tenant = Tenant.objects.create(name='first tenant')
        # create group
        self.group = Group.valid_objects.create(tenant=self.tenant, name='商务部', parent=None)
        # create user
        self.user = User.objects.create(
            first_name='Super',
            last_name='Admin',
            username='superuser',
            password=make_password('password1'),
        )
        self.user.groups.add(self.group)
        self.user.tenants.add(self.tenant)
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

    def test_group(self):
        url = '{}/api/v1/tenant/{}/contacts/group/'.format(self.service, self.tenant.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content.decode())
        results = content.get('results')
        for item in results:
            name = item.get('name')
            uuid = item.get('uuid')
            self.assertEqual(name, '商务部')
            self.assertEqual(uuid, str(self.group.uuid))

    def test_user(self):
        url = '{}/api/v1/tenant/{}/contacts/user/?group_uuid={}'.format(self.service, self.tenant.uuid, self.group.uuid)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('superuser', resp.content.decode())