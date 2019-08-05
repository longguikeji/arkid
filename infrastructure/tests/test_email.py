'''
tests for email
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    User,
    Invitation,
    AccountConfig,
    SMSConfig,
    EmailConfig,
)

EMAIL = 'a@b.com'
EMAIL_TOKEN = 'email_token'


class EmailTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.save()

        email_config = EmailConfig.get_current()
        email_config.is_valid = True
        email_config.save()

        mobile_config = SMSConfig.get_current()
        mobile_config.is_valid = True
        mobile_config.save()

    @mock.patch('infrastructure.serializers.email.redis')
    @mock.patch('infrastructure.serializers.email.send_email')
    def test_send_email(self, mock_send_email, mock_redis):
        mock_send_email.delay.return_value = None
        mock_Redis = mock.Mock()    # pylint: disable=invalid-name
        mock_Redis.get.return_value = EMAIL.encode()
        mock_Redis.set.return_value = True
        mock_redis.Redis.return_value = mock_Redis

        res = self.anonymous.json_post(reverse('infra:email', args=('register', )), data={'email': EMAIL})
        self.assertEqual(res.status_code, 201)

        res = self.anonymous.get(reverse('infra:email', args=('register', )), data={'email_token': EMAIL_TOKEN})
        expect = {'email': EMAIL}
        self.assertEqual(expect, res.json())

        new_user = User.objects.create(username='new', private_email=EMAIL)
        res = self.anonymous.json_post(reverse('infra:email', args=('reset_password', )), data={'email': EMAIL})
        self.assertEqual(res.status_code, 201)

        expect = {'email': EMAIL, 'username': 'new', 'name': ''}
        res = self.anonymous.get(reverse('infra:email', args=('reset_password', )), data={'email_token': EMAIL_TOKEN})
        self.assertEqual(expect, res.json())

        inviter = User.objects.create(username='inviter')
        invitee = new_user
        invitation = Invitation.objects.create(inviter=inviter, invitee=invitee)
        res = self.anonymous.json_post(reverse('infra:email', args=('activate_user', )), data={'key': invitation.key})
        self.assertEqual(res.status_code, 201)

        mock_Redis.hgetall.return_value = {b'email': EMAIL.encode(), b'key': invitation.key.encode()}
        mock_redis.Redis.return_value = mock_Redis
        res = self.anonymous.get(reverse('infra:email', args=('activate_user', )), data={
            'email_token': EMAIL_TOKEN
        }).json()
        self.assertIn('key', res)
        res.pop('key')
        expect = {'email': EMAIL, 'name': '', 'username': 'new'}
        self.assertEqual(expect, res)

        # update_email
        url = reverse('infra:email', args=('update_email', ))
        res = self.anonymous.json_post(url, data={'email': EMAIL})
        self.assertEqual(res.status_code, 401)
        user_a = User.create_user(username='a', password='pwd')

        self.employee = self.login_as(user_a)
        res = self.employee.json_post(url, data={'email': EMAIL, 'password': 'pwd'})
        self.assertEqual(res.status_code, 400)
        expect = {'email': ['existed']}
        self.assertEqual(res.json(), expect)

        res = self.employee.json_post(url, data={'email': '18812341234', 'password': 'wrong'})
        self.assertEqual(res.status_code, 400)
        expect = {'password': ['invalid']}
        self.assertEqual(expect, res.json())

        res = self.employee.json_post(url, data={'email': '18812341234', 'password': 'pwd'})
        self.assertEqual(res.status_code, 201)

        mock_Redis.hgetall.return_value = {b'email': b'18812341234', b'username': b'a'}
        mock_redis.Redis.return_value = mock_Redis
        res = self.employee.get(url, data={'email_token': EMAIL_TOKEN})
        expect = {'email': '18812341234', 'username': 'a', 'name': ''}
        self.assertEqual(expect, res.json())
