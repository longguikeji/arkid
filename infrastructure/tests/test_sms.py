'''
tests for sms
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

MOBILE = '18812341234'
I18N_MOBILE = '+86 18812340000'
SMS_CODE = '123456'


class SMSTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='u1', mobile=MOBILE)
        self.user_2 = User.objects.create(username='u2', mobile=I18N_MOBILE)

        account_config = AccountConfig.get_current()
        account_config.allow_register = True
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.save()

        email_config = EmailConfig.get_current()
        email_config.is_valid = True
        email_config.save()

        mobile_config = SMSConfig.get_current()
        mobile_config.is_valid = True
        mobile_config.save()

    def test_block_by_account_config(self):
        mobile_config = SMSConfig.get_current()
        mobile_config.is_valid = False
        mobile_config.save()

        res = self.anonymous.json_post(reverse('infra:sms', args=('activate_user', )), data={
            'key': '*',
        })
        self.assertEqual({'mobile': ['unsupported']}, res.json())

        account_config = AccountConfig.get_current()
        account_config.allow_register = False
        account_config.save()
        res = self.anonymous.json_post(reverse('infra:email', args=('register', )), data={
            'email': '*',
        })
        self.assertEqual({'email': ['unsupported']}, res.json())

    @mock.patch('infrastructure.serializers.sms.gen_code')
    @mock.patch('infrastructure.serializers.sms.send_sms')
    @mock.patch('infrastructure.serializers.sms.redis_conn.delete')
    @mock.patch('infrastructure.serializers.sms.redis_conn.get')
    @mock.patch('infrastructure.serializers.sms.redis_conn.set')
    def test_send_sms_to_activate_user(self, mock_redis_set, mock_redis_get, mock_redis_delete, mock_send_sms,
                                       mock_gen_code):
        mock_redis_get.return_value = SMS_CODE
        mock_redis_set.return_value = True
        mock_redis_delete.return_value = None

        mock_send_sms.return_value = True

        mock_gen_code.return_value = SMS_CODE

        inviter = User.objects.create(username='inviter')
        invitee = User.objects.create(username='invitee', mobile='18810041004')
        invitation = Invitation.objects.create(inviter=inviter, invitee=invitee)
        res = self.anonymous.json_post(reverse('infra:sms', args=('activate_user', )), data={
            'key': invitation.key,
        })
        self.assertEqual(res.status_code, 201)

        res = self.anonymous.get(reverse('infra:sms', args=('activate_user', )),
                                 data={
                                     'mobile': '18810041004',
                                     'code': SMS_CODE
                                 })
        self.assertEqual(res.status_code, 200)
        self.assertIn('sms_token', res.json())
        res = self.anonymous.get(reverse('infra:sms', args=('activate_user', )),
                                 data={
                                     'mobile': '18810041004',
                                     'code': 'wrong'
                                 })
        self.assertEqual(res.status_code, 400)

    @mock.patch('infrastructure.serializers.sms.gen_code')
    @mock.patch('infrastructure.serializers.sms.send_sms')
    @mock.patch('infrastructure.serializers.sms.redis_conn.delete')
    @mock.patch('infrastructure.serializers.sms.redis_conn.get')
    @mock.patch('infrastructure.serializers.sms.redis_conn.set')
    def test_send_sms_to_update_mobile(self, mock_redis_set, mock_redis_get, mock_redis_delete, mock_send_sms,
                                       mock_gen_code):
        mock_redis_get.return_value = SMS_CODE
        mock_redis_set.return_value = True
        mock_redis_delete.return_value = None

        mock_send_sms.return_value = True

        mock_gen_code.return_value = SMS_CODE

        url = reverse('infra:sms', args=('update_mobile', ))

        res = self.anonymous.json_post(reverse('infra:sms', args=('update_mobile', )), data={'mobile': MOBILE})
        self.assertEqual(res.status_code, 401)

        user = User.create_user(username='new', password='pwd')
        self.client = self.login_as(user)
        new_mobile = '18810041004'
        res = self.client.json_post(url, data={'mobile': MOBILE, 'password': 'pwd'})
        expect = {'mobile': ['existed']}
        self.assertEqual(expect, res.json())
        self.assertEqual(res.status_code, 400)

        res = self.client.json_post(url, data={'mobile': new_mobile, 'password': 'wrong'})
        expect = {'password': ['invalid']}
        self.assertEqual(expect, res.json())
        self.assertEqual(res.status_code, 400)

        self.client = self.login_as(user)
        res = self.client.json_post(url, data={'mobile': new_mobile, 'password': 'pwd'})
        self.assertEqual(res.status_code, 201)

        res = self.client.get(url, data={'mobile': new_mobile, 'code': SMS_CODE})
        self.assertIn('sms_token', res.json())
        self.assertEqual(res.status_code, 200)

    @mock.patch('infrastructure.serializers.sms.check_captcha')
    @mock.patch('infrastructure.serializers.sms.gen_code')
    @mock.patch('infrastructure.serializers.sms.send_sms')
    @mock.patch('infrastructure.serializers.sms.redis_conn.delete')
    @mock.patch('infrastructure.serializers.sms.redis_conn.get')
    @mock.patch('infrastructure.serializers.sms.redis_conn.set')
    def test_send_sms(self, mock_redis_set, mock_redis_get, mock_redis_delete, mock_send_sms, mock_gen_code,
                      mock_check_captcha):
        mock_redis_get.return_value = SMS_CODE
        mock_redis_set.return_value = True
        mock_redis_delete.return_value = None

        mock_send_sms.return_value = True

        mock_check_captcha.return_value = True

        mock_gen_code.return_value = SMS_CODE
        res = self.anonymous.json_post(reverse('infra:sms', args=('reset_password', )), data={
            'mobile': MOBILE,
        })
        self.assertEqual(res.status_code, 400)

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': MOBILE,
                                      'username': 'u1',
                                  })
        self.assertEqual(res.status_code, 201)

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'mobile': I18N_MOBILE,
                                      'username': 'u2',
                                  })
        self.assertEqual(res.status_code, 201)

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'mobile': '+ 86 18812341234',
                                      'username': 'u2',
                                  })
        self.assertEqual(res.status_code, 400)

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': '123',
                                      'username': 'u1',
                                  })
        self.assertEqual(res.json(), {'mobile': ['invalid']})
        self.assertEqual(res.status_code, 400)

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': '18800001234',
                                      'username': 'u1',
                                  })
        self.assertEqual(res.json(), {'mobile': ['invalid']})

        res = self.anonymous.post(reverse('infra:sms', args=('reset_password', )),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': self.user.mobile,
                                      'username': 'u1',
                                  })
        self.assertEqual(res.status_code, 201)

        # register
        exist_mobile = '18800001234'
        User.objects.create(username='any', mobile=exist_mobile)
        res = self.anonymous.post(reverse('infra:sms', args=('register', )),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': exist_mobile,
                                  })
        self.assertEqual(res.json(), {'mobile': ['existed']})

        # logined
        res = self.client.post(reverse('infra:sms', args=('reset_password', )),
                               data={
                                   'mobile': MOBILE,
                                   'username': 'u1',
                               })

        self.assertEqual(res.status_code, 201)

        res = self.anonymous.get(reverse('infra:sms', args=('reset_password', )),
                                 data={
                                     'mobile': MOBILE,
                                     'code': SMS_CODE
                                 })

        self.assertEqual(res.status_code, 200)

        res = self.anonymous.get(reverse('infra:sms', args=('reset_password', )),
                                 data={
                                     'mobile': MOBILE,
                                     'code': 'wrong code'
                                 })
        self.assertEqual(res.status_code, 400)

        # common
        res = self.anonymous.post(reverse('infra:common_sms'),
                                  data={
                                      'captcha': '.',
                                      'captcha_key': '.',
                                      'mobile': '18810101010',
                                  })
        self.assertEqual(res.status_code, 201)

    @mock.patch('infrastructure.serializers.sms.gen_code')
    @mock.patch('infrastructure.serializers.sms.send_sms')
    @mock.patch('infrastructure.serializers.sms.redis_conn.delete')
    @mock.patch('infrastructure.serializers.sms.redis_conn.get')
    @mock.patch('infrastructure.serializers.sms.redis_conn.set')
    def test_send_sms_to_ding_bind(self, mock_redis_set, mock_redis_get, mock_redis_delete, mock_send_sms,
                                   mock_gen_code):
        mock_redis_get.return_value = SMS_CODE
        mock_redis_set.return_value = True
        mock_redis_delete.return_value = None

        mock_send_sms.return_value = True

        mock_gen_code.return_value = SMS_CODE

        url = reverse('infra:sms', args=('ding_bind', ))

        res = self.anonymous.json_post(reverse('infra:sms', args=('update_mobile', )), data={'mobile': MOBILE})
        self.assertEqual(res.status_code, 401)

        res = self.client.get(url, data={'mobile': MOBILE, 'code': SMS_CODE})
        self.assertIn('sms_token', res.json())
        self.assertEqual(res.status_code, 200)
