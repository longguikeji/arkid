'''
tests for api about admin
'''
# pylint: disable=missing-docstring

from django.urls import reverse
from django.utils import timezone

from siteapi.v1.tests import TestCase
from drf_expiring_authtoken.settings import token_settings


class AdminTestCase(TestCase):
    def test_access_admin_reject(self):
        res = self.anonymous.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 401)

    def test_access_admin_success(self):
        res = self.anonymous.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 401)

        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 200)

    def test_token_expired(self):
        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 200)

        token = self.user.auth_token
        token.created = timezone.now() - token_settings.EXPIRING_TOKEN_LIFESPAN * 2
        token.save()

        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 401)

    def test_admin_required(self):
        self.user.username = 'test_client'
        self.user.is_boss = False
        self.user.save()

        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 403)

        res = self.client.get(reverse('siteapi:config'))
        self.assertEqual(res.status_code, 403)

        self.user.username = 'admin'
        self.user.save()

    def test_header_arker_auth(self):
        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )))
        self.assertEqual(res.status_code, 200)

        header = {'HTTP_ARKER': 'portal'}
        res = self.anonymous.get(reverse('siteapi:dept_tree', args=('root', )), **header)
        self.assertEqual(res.status_code, 401)

        header = {'HTTP_ARKER': 'oneid_broker'}
        res = self.anonymous.get(reverse('siteapi:dept_tree', args=('root', )), **header)
        self.assertEqual(res.status_code, 200)
