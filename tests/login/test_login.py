#!/usr/bin/env python3

from unittest import mock
from django.test import TestCase

from tenant.models import Tenant
from extension.models import Extension
from inventory.models import User
from django.contrib.auth.hashers import make_password
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from app.models import App
from common.code import Code
from runtime import get_app_runtime
from api.v1.serializers.sms import LoginSMSClaimSerializer

import json

from extension_root.redis_cache import extension
from django.conf import settings


class LoginTestCase(TestCase):
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
        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.runtime = get_app_runtime()
        extension.start(self.runtime)

    def test_username_login(self):
        tenant_uuid = self.tenant.uuid
        field_names = 'username'
        field_uuids = ''
        url = (
            reverse("api:tenant-secret-login", args=[tenant_uuid])
            + f'?field_names={field_names}&field_uuids={field_uuids}'
        )
        body = {'username': 'superuser', 'password': 'password1'}
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        error = result.get('error')
        self.assertEqual(error, Code.OK.value)

    def test_mobile_login(self):
        user = User.valid_objects.filter(username='superuser').first()
        mobile = '18011112222'
        user.mobile = mobile
        user.save()
        tenant_uuid = self.tenant.uuid
        r = get_app_runtime()
        key = LoginSMSClaimSerializer.gen_sms_code_key(mobile)
        value = '222333'
        self.runtime.cache_provider.set(key, value, settings.SMS_LIFESPAN.seconds)
        url = reverse(
            "api:tenant-mobile-login",
            args=[
                tenant_uuid,
            ],
        )
        body = {'mobile': mobile, 'code': value}
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
        result = json.loads(resp.content.decode())
        error = result.get('error')
        self.assertEqual(error, Code.OK.value)
