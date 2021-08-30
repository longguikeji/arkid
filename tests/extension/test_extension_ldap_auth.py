'''
test extension register
'''
import json
from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from extension.models import Extension
from inventory.models import User
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
            type='ldap_auth',
        )
        # reload extension required
        reload_extension('ldap_auth', is_add=True)
        # ldap_auth config
        self.data = {
            'bind_dn': 'cn=admin,dc=example,dc=org',
            'use_tls': False,
            'server_uri': 'ldap://localhost:10389',
            'user_base_dn': 'ou=users,o=auth,dc=example,dc=org',
            'bind_password': 'Qishibushi34',
            'user_attr_map': {
                'username': 'cn',
                'first_name': 'givenName',
                'last_name': 'sn',
                'email': 'mail'
            },
            'user_object_class': 'inetOrgPerson',
        }

        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))

    def test_extension_create(self):
        url = '/api/v1/tenant/{}/authorization_agent/'.format(self.tenant.uuid)
        body = {'is_active': True, 'type': 'ldap_auth', 'data': self.data}
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))
        self.assertEqual(result.get('data'), self.data)

    def test_extension_delete(self):
        # create ldap_auth AuthorizationAgent
        authorization_agent = AuthorizationAgent.objects.create(
            tenant=self.tenant,
            type='ldap_auth',
            data=self.data,
        )
        url = '/api/v1/tenant/{}/authorization_agent/{}/'.format(self.tenant.uuid, authorization_agent.uuid)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 204, resp.content.decode())

    @mock.patch('django_python3_ldap.ldap.LDAPConnection.authenticate')
    @mock.patch('django_python3_ldap.ldap.LDAPConnection.get_connection')
    def test_authenticate(self, get_connection, authenticate):
        # create ldap_auth AuthorizationAgent
        authorization_agent = AuthorizationAgent.objects.create(
            tenant=self.tenant,
            type='ldap_auth',
            data=self.data,
        )

        get_connection.rerun_value = None

        r = get_app_runtime()
        provider_cls = r.authorization_agent_providers.get('ldap_auth')
        agent = provider_cls()
        username = 'test3'
        password = 'passwd'
        user = agent.authenticate(None, self.tenant.uuid, username, password)
        authenticate.assert_called_with(username=username, password=password)
