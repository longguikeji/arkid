'''
tests for api about qq qr
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (User, AccountConfig, QqConfig, QqUser)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.allow_qq_qr = True
        account_config.save()

        qq_config = QqConfig.get_current()
        qq_config.qr_app_valid = True
        qq_config.save()

    @mock.patch("thirdparty_data_sdk.qq_sdk.qq_openid_sdk.QqInfoManager.get_open_id")
    def test_qq_qr_login(self, mock_get_open_id):
        qq_config = QqConfig.get_current()
        qq_config.__dict__.update(app_id='test_app_id', app_key='test_app_key', redirect_uri='test_redirect_uri',\
            qr_app_valid=True)
        qq_config.save()
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        open_id = 'test_open_id'
        qq_user = QqUser.valid_objects.create(open_id=open_id, user=user)
        qq_user.save()
        client = self.client
        mock_get_open_id.return_value = 'test_open_id'

        res = client.post(reverse('siteapi:qq_qr_callback'),\
            data={'code':'test_code', 'redirect_uri':'test_redirect_uri'})

        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.json())

    @mock.patch("thirdparty_data_sdk.qq_sdk.qq_openid_sdk.QqInfoManager.get_open_id")
    def test_qq_qr_login_newuser(self, mock_get_open_id):    # pylint: disable=invalid-name
        qq_config = QqConfig.get_current()
        qq_config.__dict__.update(app_id='test_app_id', app_key='test_app_key', redirect_uri='test_redirect_uri',\
            qr_app_valid=True)
        qq_config.save()
        mock_get_open_id.return_value = 'unregistered_open_id'
        client = self.client
        res = client.post(reverse('siteapi:qq_qr_callback'),\
            data={'code':'test_code', 'app_id':'test_app_id', 'redirect_uri':'test_redirect_uri'})
        expect = {'token': '', 'third_party_id': 'unregistered_open_id'}
        self.assertEqual(res.json(), expect)

    def test_qq_qr_login_forbidden(self):
        client = self.client
        qq_config = QqConfig.get_current()
        qq_config.__dict__.update(app_id='app_id', app_private_key='app_private_key',\
            qq_public_key='qq_public_key', qr_app_valid=False)
        qq_config.save()
        res = client.post(reverse('siteapi:qq_qr_callback'),\
            data={'code':'test_code', 'app_id':'test_app_id', 'redirect_uri':'test_redirect_uri'})
        expect_json = {'err_msg': 'qq qr not allowed'}
        expect_code = 403
        self.assertEqual(res.json(), expect_json)
        self.assertEqual(res.status_code, expect_code)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_qq_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:qq_bind'), data={'sms_token':\
            'test_sms_token', 'user_id':'test_open_id', 'redirect_uri':'test_redirect_uri'})
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_qq_register_bind(self, mock_check_sms_token, mock_clear_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        mock_clear_sms_token.return_value = None
        res = client.post(reverse('siteapi:qq_register_bind'),
                          data={
                              'username': 'username',
                              'password': 'password',
                              'sms_token': 'test_sms_token',
                              'user_id': 'test_open_id'
                          })
        self.assertEqual(res.status_code, 201)
        self.assertIn('token', res.json())
