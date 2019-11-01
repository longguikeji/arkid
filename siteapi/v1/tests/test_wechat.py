'''
tests for api about wechat qr
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (User, AccountConfig, WechatConfig, WechatUser)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.allow_wechat_qr = True
        account_config.save()

        wechat_config = WechatConfig.get_current()
        wechat_config.qr_app_valid = True
        wechat_config.save()

    @mock.patch('thirdparty_data_sdk.wechat_sdk.wechat_user_info_manager.WechatUserInfoManager.get_union_id')
    def test_wechat_qr_login(self, mock_get_union_id):
        mock_get_union_id.return_value = 'test_wechat_user_id'

        wechat_config = WechatConfig.get_current()
        wechat_config.__dict__.update(appid='test_appid', secret='test_secret', qr_app_valid=True)
        wechat_config.save()

        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()

        unionid = 'test_wechat_user_id'
        wechat_user = WechatUser.valid_objects.create(unionid=unionid, user=user)
        wechat_user.save()

        client = self.client
        res = client.post(reverse('siteapi:wechat_qr_callback'),\
            data={'code':'test_auth_code'})

        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.json())

    @mock.patch('thirdparty_data_sdk.wechat_sdk.wechat_user_info_manager.WechatUserInfoManager.get_union_id')
    def test_wechat_qr_login_newuser(self, mock_get_union_id):    # pylint: disable=invalid-name
        wechat_config = WechatConfig.get_current()
        wechat_config.__dict__.update(app_id='test_app_id', app_private_key='test_app_private_key',\
            wechat_public_key='test_wechat_public_key', qr_app_valid=True)
        wechat_config.save()
        mock_get_union_id.return_value = ''
        client = self.client
        res = client.post(reverse('siteapi:wechat_qr_callback'),\
            data={'code':'test_auth_code', 'app_id':'test_app_id'})
        expect = {'token': '', 'third_party_id': ''}
        self.assertEqual(res.json(), expect)

    def test_wechat_qr_login_forbidden(self):    # pylint: disable=invalid-name
        client = self.client
        wechat_config = WechatConfig.get_current()
        wechat_config.__dict__.update(app_id='app_id', app_private_key='app_private_key',\
            wechat_public_key='wechat_public_key', qr_app_valid=False)
        wechat_config.save()
        res = client.post(reverse('siteapi:wechat_qr_callback'),\
            data={'code':'test_auth_code'})
        expect_json = {'err_msg': 'wechat qr not allowed'}
        expect_code = 403
        self.assertEqual(res.json(), expect_json)
        self.assertEqual(res.status_code, expect_code)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_wechat_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:wechat_bind'), data={'sms_token':\
            'test_sms_token', 'user_id':'test_wechat_user_id'})
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_wechat_register_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:wechat_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_wechat_user_id'
                          })
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())
