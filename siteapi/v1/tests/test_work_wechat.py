'''
tests for api about work_wechat qr
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (User, AccountConfig, WorkWechatConfig, WorkWechatUser)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.allow_work_wechat_qr = True
        account_config.save()

        work_wechat_config = WorkWechatConfig.get_current()
        work_wechat_config.qr_app_valid = True
        work_wechat_config.save()

    @mock.patch('thirdparty_data_sdk.work_wechat_sdk.user_info_manager.WorkWechatManager.get_work_wechat_user_id')
    def test_work_wechat_qr_login(self, mock_get_work_wechat_user_id):
        mock_get_work_wechat_user_id.return_value = 'test_work_wechat_user_id'
        work_wechat_config = WorkWechatConfig.get_current()
        work_wechat_config.__dict__.update(corp_id='test_corp_id', secret='test_secret', qr_app_valid=True)
        work_wechat_config.save()

        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()

        test_id = 'test_work_wechat_user_id'
        work_wechat_user = WorkWechatUser.valid_objects.create(work_wechat_user_id=test_id, user=user)
        work_wechat_user.save()

        client = self.client
        res = client.post(reverse('siteapi:work_wechat_qr_callback'),\
            data={'code':'test_auth_code'})
        self.assertEqual(res.status_code, 200)
        self.assertIsNot('', res.json()['token'])

    @mock.patch('thirdparty_data_sdk.work_wechat_sdk.user_info_manager.WorkWechatManager.get_work_wechat_user_id')
    def test_work_wechat_qr_login_newuser(self, mock_get_work_wechat_user_id):    # pylint: disable=invalid-name
        work_wechat_config = WorkWechatConfig.get_current()
        work_wechat_config.__dict__.update(app_id='test_app_id', app_private_key='test_app_private_key',\
            work_wechat_public_key='test_work_wechat_public_key', qr_app_valid=True)
        work_wechat_config.save()
        mock_get_work_wechat_user_id.return_value = 'test_work_wechat_user_id'
        client = self.client
        res = client.post(reverse('siteapi:work_wechat_qr_callback'),\
            data={'code':'test_auth_code'})
        expect = {'token': '', 'third_party_id': 'test_work_wechat_user_id'}
        self.assertEqual(res.json(), expect)

    def test_work_wechat_qr_login_forbidden(self):    # pylint: disable=invalid-name
        account_config = AccountConfig.get_current()
        account_config.allow_work_wechat_qr = False
        account_config.save()
        work_wechat_config = WorkWechatConfig.get_current()
        work_wechat_config.__dict__.update(corp_id='test_corp_id', agent_id='test_agent_id',\
            secret='test_secret', qr_app_valid=False)
        work_wechat_config.save()
        client = self.client
        res = client.post(reverse('siteapi:work_wechat_qr_callback'), data={'code': 'test_auth_code'})
        expect = {'err_msg': 'work wechat qr not allowed'}
        expect_code = 403
        self.assertEqual(res.json(), expect)
        self.assertEqual(res.status_code, expect_code)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_work_wechat_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:work_wechat_bind'), data={'sms_token':\
            'test_sms_token', 'user_id':'test_work_wechat_user_id'})
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_work_wechat_register_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:work_wechat_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_work_wechat_user_id'
                          })
        self.assertEqual(res.status_code, 201)
        self.assertIsNot('', res.json()['token'])
