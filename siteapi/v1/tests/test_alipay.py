'''
tests for api about alipay qr
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (User, AccountConfig, AlipayConfig, AlipayUser)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.allow_alipay_qr = True
        account_config.save()

        alipay_config = AlipayConfig.get_current()
        alipay_config.qr_app_valid = True
        alipay_config.save()

    @mock.patch("thirdparty_data_sdk.alipay_api.alipay_sdk.get_alipay_id")
    def test_alipay_qr_login(self, mock_get_alipay_id):
        alipay_config = AlipayConfig.get_current()
        alipay_config.__dict__.update(app_id='test_app_id', app_private_key='test_app_private_key',\
            alipay_public_key='test_alipay_public_key', qr_app_valid=True)
        alipay_config.save()
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        alipay_id = 'test_alipay_id'
        alipay_user = AlipayUser.valid_objects.create(alipay_id=alipay_id, user=user)
        alipay_user.save()
        client = self.client
        mock_get_alipay_id.side_effect = ['test_alipay_id']

        res = client.post(reverse('siteapi:alipay_qr_callback'),\
            data={'auth_code':'test_auth_code', 'app_id':'test_app_id'})
        expect = [
            'token', 'uuid', 'user_id', 'username', 'name', 'email', 'mobile', 'employee_number', 'gender', 'perms',
            'avatar', 'roles', 'private_email', 'position', 'is_settled', 'is_manager', 'is_admin', 'is_extern_user',
            'origin_verbose'
        ]
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res_keys, expect)

    @mock.patch("thirdparty_data_sdk.alipay_api.alipay_sdk.get_alipay_id")
    def test_alipay_qr_login_newuser(self, mock_get_alipay_id):    # pylint: disable=invalid-name
        alipay_config = AlipayConfig.get_current()
        alipay_config.__dict__.update(app_id='test_app_id', app_private_key='test_app_private_key',\
            alipay_public_key='test_alipay_public_key', qr_app_valid=True)
        alipay_config.save()
        mock_get_alipay_id.side_effect = ['unregistered_alipay_id']
        client = self.client
        res = client.post(reverse('siteapi:alipay_qr_callback'),\
            data={'auth_code':'test_auth_code', 'app_id':'test_app_id'})
        expect = {'token': '', 'alipay_id': 'unregistered_alipay_id'}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_alipay_query_user_newuser(self, mock_check_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:alipay_query_user'), data={'sms_token': '123132132131'})
        expect = {'exist': False}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_alipay_query_user_registered(self, mock_check_sms_token):    # pylint: disable=invalid-name
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:alipay_query_user'), data={'sms_token': 'test_sms_token'})
        expect = {'exist': True}
        self.assertEqual(res.json(), expect)

    def test_alipay_qr_login_forbidden(self):
        client = self.client
        alipay_config = AlipayConfig.get_current()
        alipay_config.__dict__.update(app_id='app_id', app_private_key='app_private_key',\
            alipay_public_key='alipay_public_key', qr_app_valid=False)
        alipay_config.save()
        res = client.post(reverse('siteapi:alipay_qr_callback'),\
            data={'auth_code':'test_auth_code', 'app_id':'test_app_id'})
        expect_json = {'err_msg': 'alipay qr not allowed'}
        expect_code = 403
        self.assertEqual(res.json(), expect_json)
        self.assertEqual(res.status_code, expect_code)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_alipay_bind(self, mock_check_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:alipay_bind'), data={'sms_token':\
            'test_sms_token', 'alipay_id':'test_alipay_id'})
        expect = ['token', 'uuid', 'user_id', 'username', 'name', 'email', 'mobile',\
            'employee_number', 'gender', 'perms', 'avatar', 'roles',\
                'private_email', 'position', 'is_settled', 'is_manager', 'is_admin', 'is_extern_user', 'origin_verbose']
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_keys, expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_alipay_register_bind(self, mock_check_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        res = client.post(reverse('siteapi:alipay_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'alipay_id': 'test_alipay_id'
                          })
        expect = ['uuid', 'user_id', 'username', 'name', 'email', 'mobile', 'employee_number',\
            'gender', 'perms', 'avatar', 'roles', 'private_email', 'position', 'is_settled',\
                'is_manager', 'is_admin', 'is_extern_user', 'origin_verbose', 'token']
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_keys, expect)
