#!/usr/bin/env python3
import json
from django.test import TestCase, Client
from tenant.models import Tenant
from django.contrib.auth.hashers import make_password
from inventory.models import User
from django.urls import reverse
from webhook.models import Webhook, WebhookEvent


class TestWebhookApi(TestCase):
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
        print(token)

    def create_webhook(self):
        hook = Webhook.valid_objects.create(
            name='hook1',
            url='http://www.test.com/target',
            secret='test123',
            tenant=self.tenant,
        )
        WebhookEvent.valid_objects.create(event_type='any_events', webhook=hook)
        return hook

    def test_create_webhook(self):
        url = '/api/v1/tenant/{}/webhook/'.format(self.tenant.uuid)
        body = {
            'name': 'hook1',
            'url': 'http://www.test.com/target',
            'events': ['any_events'],
            'secret': 'test123',
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 201, resp.content.decode())
        result = json.loads(resp.content.decode())
        self.assertIsNotNone(result.get('uuid'))

    def test_update_wehook(self):
        hook = self.create_webhook()
        events = hook.events.all()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, 'any_events')
        url = '/api/v1/tenant/{}/webhook/{}/'.format(self.tenant.uuid, hook.uuid)
        body = {
            'name': 'hook2',
            'events': ['user_created', 'user_updated'],
            'url': 'http://www.test.com/target1',
        }

        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

        hook = Webhook.valid_objects.all().first()
        self.assertEqual(hook.name, 'hook2')
        self.assertEqual(hook.url, 'http://www.test.com/target1')
        events = hook.events.all()
        self.assertEqual(
            set([e.event_type for e in events]), set(['user_created', 'user_updated'])
        )

    def test_delete_webhook(self):
        hook = self.create_webhook()
        url = '/api/v1/tenant/{}/webhook/{}/'.format(self.tenant.uuid, hook.uuid)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204, resp.content.decode())
        is_exists = Webhook.valid_objects.all().exists()
        self.assertEqual(is_exists, False)

    def test_retrive_webhook(self):
        hook = self.create_webhook()
        url = '/api/v1/tenant/{}/webhook/{}/'.format(self.tenant.uuid, hook.uuid)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        expected = {
            'uuid': hook.uuid.hex,
            'name': 'hook1',
            'events': ['any_events'],
            'url': 'http://www.test.com/target',
            'secret': 'test123',
        }
        self.assertEqual(result, expected)

    def test_list_webhook(self):
        hook = self.create_webhook()
        url = '/api/v1/tenant/{}/webhook/'.format(self.tenant.uuid)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        expected = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'uuid': hook.uuid.hex,
                    'name': 'hook1',
                    'events': ['any_events'],
                    'url': 'http://www.test.com/target',
                    'secret': 'test123',
                }
            ],
        }
        self.assertEqual(result, expected)
