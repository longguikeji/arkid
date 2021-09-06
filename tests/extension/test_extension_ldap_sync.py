'''
test extension register
'''
import json
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from extension.models import Extension
from inventory.models import User, Group
from authorization_agent.models import AuthorizationAgent
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from app.models import App
from runtime import get_app_runtime
from extension.utils import reload_extension


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
            type='ldap_sync',
        )
        # reload extension required
        reload_extension('ldap_sync', is_add=True)
        # ldap_sync config
        self.data = {
            'bind_dn': 'cn=admin,dc=example,dc=org',
            'use_tls': False,
            'server_uri': 'ldap://localhost:10389',
            'user_base_dn': 'ou=users,o=auth,dc=example,dc=org',
            'group_base_dn': 'ou=groups,o=auth,dc=example,dc=org',
            'bind_password': 'Qishibushi34',
            'user_attr_map': {
                'username': 'cn',
                'first_name': 'givenName',
                'last_name': 'sn',
                'email': 'mail'
            },
            'group_attr_map': {
                'name': 'cn'
            },
            'user_object_class': 'inetOrgPerson',
            'group_object_class': 'groupOfNames',
        }

        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_extension_create(self):
        url = '/api/v1/tenant/{}/authorization_agent/'.format(self.tenant.uuid)
        body = {'is_active': True, 'type': 'ldap_sync', 'data': self.data}
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
        self.assertEqual(result.get('data'), self.data)

    def test_extension_delete(self):
        # create ldap_sync AuthorizationAgent
        authorization_agent = AuthorizationAgent.objects.create(
            tenant=self.tenant,
            type='ldap_sync',
            data=self.data,
        )
        url = '/api/v1/tenant/{}/authorization_agent/{}/'.format(self.tenant.uuid, authorization_agent.uuid)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())

    @mock.patch('extension_root.ldap_sync.tasks.ldap_sync_user')
    def test_ldap_sync_create_user(self, ldap_sync_user):
        """
        Test create user
        """
        # create user
        ford = User.objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )

        ford.tenants.add(self.tenant)

        ford.save()

        ldap_sync_user.assert_called_with(self.tenant.uuid, ford.id, False)

    @mock.patch('extension_root.ldap_sync.tasks.ldap_sync_user')
    def test_ldap_sync_delete_user(self, ldap_sync_user):
        """
        Test delete user
        """
        # create user
        ford = User.objects.create(
            first_name='Robert',
            last_name='Ford',
            username='rford',
            email='rford@ww.com',
        )

        ford.tenants.add(self.tenant)

        User.objects.filter(username='rford').delete()

        ldap_sync_user.assert_called_with(self.tenant.uuid, ford.id, True)

    @mock.patch('extension_root.ldap_sync.tasks.ldap_sync_group')
    def test_ldap_sync_create_group(self, ldap_sync_group):
        """
        Test create group
        """
        # create group
        behavior = Group.objects.create(name='Behavior Group', tenant=self.tenant)

        behavior.save()

        ldap_sync_group.assert_called_with(self.tenant.uuid, behavior.id, False)

    @mock.patch('extension_root.ldap_sync.tasks.ldap_sync_group')
    def test_ldap_sync_delete_group(self, ldap_sync_group):
        """
        Test delete group
        """
        # create group
        behavior = Group.objects.create(name='Behavior Group', tenant=self.tenant)

        Group.objects.filter(name='Behavior Group').delete()

        User.objects.filter(username='rford').delete()

        ldap_sync_group.assert_called_with(self.tenant.uuid, behavior.id, True)
