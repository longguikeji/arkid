#!/usr/bin/env python3
import json
from django.test import TestCase, Client, TransactionTestCase
from tenant.models import Tenant
from django.contrib.auth.hashers import make_password
from inventory.models import User, Group
from app.models import App
from django.urls import reverse
from webhook.models import Webhook, WebhookEvent
from unittest import mock
from runtime import get_app_runtime
from common.provider import AppTypeProvider


class TestUserWebhookEvents(TransactionTestCase):
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
        token = self.user.token
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(token))

    @mock.patch('webhook.manager.WebhookManager.user_created')
    def test_user_created_event(self, user_created):
        url = '/api/v1/tenant/{}/user/'.format(self.tenant.uuid)
        body = {
            "username": "user1",
            "set_groups": [],
            "set_permissions": [],
            "custom_user": {"data": {}},
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())

        user = User.valid_objects.filter(username='user1').first()
        self.assertIsNotNone(user)

        user_created.assert_called_with(self.tenant.uuid, user)

    @mock.patch('webhook.manager.WebhookManager.user_updated')
    def test_user_updated_event(self, user_updated):
        user1 = User.valid_objects.create(username='user1')
        user1.tenants.add(self.tenant)
        user1.save()
        uuid = user1.uuid
        url = '/api/v1/tenant/{}/user/{}/'.format(self.tenant.uuid, user1.uuid)
        body = {
            "username": "user2",
            "set_groups": [],
            "set_permissions": [],
            "custom_user": {"data": {}},
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        user = User.valid_objects.filter(username='user2').first()
        user_updated.assert_called_with(self.tenant.uuid, user)

    @mock.patch('webhook.manager.WebhookManager.user_deleted')
    def test_user_deleted_event(self, user_deleted):
        user1 = User.valid_objects.create(username='user1')
        user1.tenants.add(self.tenant)
        user1.save()
        uuid = user1.uuid
        url = '/api/v1/tenant/{}/user/{}/'.format(self.tenant.uuid, user1.uuid)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        user_deleted.assert_called_with(self.tenant.uuid, user1)

    @mock.patch('webhook.manager.WebhookManager.group_created')
    def test_group_created_event(self, group_created):
        url = '/api/v1/tenant/{}/group/'.format(self.tenant.uuid)
        body = {"name": "group1", "set_permissions": []}
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())

        group = Group.valid_objects.filter(name='group1').first()
        self.assertIsNotNone(group)

        group_created.assert_called_with(self.tenant.uuid, group)

    @mock.patch('webhook.manager.WebhookManager.group_updated')
    def test_group_updated_event(self, group_updated):
        group = Group.valid_objects.create(name='group1', tenant=self.tenant)
        uuid = group.uuid
        url = '/api/v1/tenant/{}/group/{}/'.format(self.tenant.uuid, group.uuid)
        body = {"name": "group2", "set_permissions": []}
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        group = Group.valid_objects.filter(name='group2').first()
        group_updated.assert_called_with(self.tenant.uuid, group)

    @mock.patch('webhook.manager.WebhookManager.group_deleted')
    def test_group_deleted_event(self, group_deleted):
        group = Group.valid_objects.create(name='group1', tenant=self.tenant)
        uuid = group.uuid
        url = '/api/v1/tenant/{}/group/{}/'.format(self.tenant.uuid, group.uuid)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204, resp.content.decode())
        group_deleted.assert_called_with(self.tenant.uuid, group)

    @mock.patch('webhook.manager.WebhookManager.app_created')
    def test_app_created_event(self, app_created):
        class TestAppProvider(AppTypeProvider):
            def create(self, app, data):
                pass

            def update(self, app, data):
                pass

        r = get_app_runtime()
        r.register_app_type('test', 'test', TestAppProvider, None)
        url = '/api/v1/tenant/{}/app/'.format(self.tenant.uuid)
        body = {
            'name': 'app1',
            'url': '',
            'logo': '',
            'description': '',
            'type': 'test',
            'data': {},
            'auth_tmpl': '',
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())

        app = App.valid_objects.filter(name='app1').first()
        self.assertIsNotNone(app)

        app_created.assert_called_with(self.tenant.uuid, app)

    @mock.patch('webhook.manager.WebhookManager.app_updated')
    def test_app_updated_event(self, app_updated):
        app = App.valid_objects.create(name='app1', type='test', tenant=self.tenant)

        class TestAppProvider(AppTypeProvider):
            def create(self, app, data):
                pass

            def update(self, app, data):
                pass

        r = get_app_runtime()
        r.register_app_type('test', 'test', TestAppProvider, None)
        url = '/api/v1/tenant/{}/app/{}/'.format(self.tenant.uuid, app.uuid)
        body = {
            'name': 'app2',
            'url': '',
            'logo': '',
            'description': '',
            'type': 'test',
            'data': {},
            'auth_tmpl': '',
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

        app = App.valid_objects.filter(name='app2').first()
        self.assertIsNotNone(app)

        app_updated.assert_called_with(self.tenant.uuid, app)

    @mock.patch('webhook.manager.WebhookManager.app_deleted')
    def test_app_deleted_event(self, app_deleted):
        app = App.valid_objects.create(name='app1', tenant=self.tenant)
        uuid = app.uuid
        url = '/api/v1/tenant/{}/app/{}/'.format(self.tenant.uuid, app.uuid)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204, resp.content.decode())
        app_deleted.assert_called_with(self.tenant.uuid, app)
