'''
tests for api about ding qr
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from ....siteapi.v1.tests import TestCase
from ....oneid_meta.models import (User, DingUser, AccountConfig, DingConfig)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.allow_ding_qr = True
        account_config.save()

        ding_config = DingConfig.get_current()
        ding_config.qr_app_valid = True
        ding_config.save()

    @mock.patch("thirdparty_data_sdk.dingding.dingsdk.ding_id_manager.DingIdManager.get_ding_id")
    def test_ding_qr_login(self, mock_get_ding_id):
        ding_config = DingConfig.get_current()
        ding_config.__dict__.update(qr_app_id='qr_app_id', qr_app_secret='qr_app_secret', qr_app_valid=True)
        ding_config.save()
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        ding_id = 'test_ding_id'
        ding_user = DingUser.valid_objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        client = self.client
        mock_get_ding_id.side_effect = ['test_ding_id']

        res = client.post(reverse('siteapi:ding_qr_callback'), data={'code': 'CODE...........', 'state': 'STATE'})
        self.assertIsNot('', res.json()['token'])

    @mock.patch("thirdparty_data_sdk.dingding.dingsdk.ding_id_manager.DingIdManager.get_ding_id")
    def test_ding_qr_login_newuser(self, mock_get_ding_id):
        client = self.client
        mock_get_ding_id.side_effect = ['unregistered_dingid']
        res = client.post(reverse('siteapi:ding_qr_callback'), data={'code': 'CODE...........', 'state': 'STATE'})
        expect = {'token': '', 'third_party_id': 'unregistered_dingid'}
        self.assertEqual(res.json(), expect)

    def test_ding_qr_login_forbidden(self):
        client = self.client
        ding_config = DingConfig.get_current()
        ding_config.__dict__.update(qr_app_id='qr_app_id', qr_app_secret='qr_app_secret', qr_app_valid=False)
        ding_config.save()
        res = client.post(reverse('siteapi:ding_qr_callback'), data={'code': 'CODE...........', 'state': 'STATE'})
        expect_json = {'err_msg': 'ding qr not allowed'}
        expect_code = 403
        self.assertEqual(res.json(), expect_json)
        self.assertEqual(res.status_code, expect_code)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_ding_query_user(self, mock_clear_sms_token, mock_check_sms_token):
        client = self.client
        mock_clear_sms_token.return_value = True
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:qr_query_user'), data={'sms_token': '123132132131'})
        expect = {'exist': False}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_ding_query_user_loguped(self, mock_clear_sms_token, mock_check_sms_token):
        client = self.client
        mock_clear_sms_token.return_value = True
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:qr_query_user'), data={'sms_token': 'test_sms_token'})
        expect = {'exist': True}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_ding_bind(self, mock_clear_sms_token, mock_check_sms_token):
        client = self.client
        mock_clear_sms_token.return_value = True
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:ding_bind'), data={'sms_token':\
            'test_sms_token', 'user_id':'ding_idding_id'})
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_ding_register_bind(self, mock_clear_sms_token, mock_check_sms_token):
        client = self.client
        mock_clear_sms_token.return_value = True
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_patch_name(self, mock_clear_sms_token, mock_check_sms_token):
        client = self.client
        mock_clear_sms_token.return_value = True
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        patch_data = {
            'username': 'username',
            'name': 'new_name',
            'ding_usre': {
                'account': "",
                'uid': "",
                'data': "{}"
            },
        }
        res = client.json_patch(reverse('siteapi:user_detail', args=('username', )), patch_data)
        self.assertEqual(res.status_code, 200)
        res = res.json()['user']
        self.assertIn('new_name', res['name'])

    def test_ding_qr_register_forbidden(self):
        client = self.client
        account_config = AccountConfig.get_current()
        account_config.allow_register = False
        account_config.save()
        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        expect = {'err_msg': 'ding qr register not allowed'}
        self.assertEqual(res.json(), expect)
        self.assertEqual(res.status_code, 403)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_ding_bind_user_exist(self, mock_check_sms_token, mock_clear_sms_token):
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        ding_user = DingUser.objects.create(user=user)
        ding_user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:ding_bind'), data={'sms_token':\
            'test_sms_token', 'user_id':'test_ding_id'})
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    def test_qr_register_invalid_username(self, mock_clear_sms_token, mock_check_sms_token):    # pylint: disable=invalid-name
        client = self.client
        mock_clear_sms_token.return_value = True
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': '123',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 400)

        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': '12345678901234567',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 400)

        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': '@#%@%@53@22432',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['invalid']})

        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': '中文注册',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['invalid']})

        res = client.post(reverse('siteapi:ding_register_bind'),
                          data={
                              'username': 'REWTWE',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_ding_id'
                          })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['invalid']})
