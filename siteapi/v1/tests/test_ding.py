'''
tests for api about ucenter
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    User,
    DingUser,
    AccountConfig,
    EmailConfig,
    SMSConfig,
    DingConfig
)


MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class UCenterTestCase(TestCase):
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


    @mock.patch("siteapi.v1.views.sns.DingQrCallbackView.get_ding_id")
    def test_ding_sns_login(self, mock_get_ding_id):
        ding_config = DingConfig.get_current()
        ding_config.__dict__.update(qr_app_id='qr_app_id', qr_app_secret='qr_app_secret', qr_app_valid=True)
        ding_config.save()
        accont_config = AccountConfig.get_current()
        accont_config.allow_ding_qr = True
        accont_config.save()
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        ding_id = 'ding_idding_id'
        ding_user = DingUser.valid_objects.create(ding_id=ding_id, user=user)
        ding_user.save()
        client = self.client
        mock_get_ding_id.side_effect = [{'ding_id': 'ding_idding_id',\
            'openid': 'openidopenid', 'unionid': 'unionidunionid'}]

        res = client.post(reverse('siteapi:ding_qr_callback'), data={'code':'CODE...........', 'state':'STATE'})
        expect = ['token', 'uuid', 'user_id', 'username', 'name', 'email', 'mobile',\
            'employee_number', 'gender', 'ding_user', 'perms', 'avatar', 'roles',\
                'private_email', 'position', 'is_settled', 'is_manager', 'is_admin', 'is_extern_user', 'origin_verbose']
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res_keys, expect)

    @mock.patch("siteapi.v1.views.sns.DingQrCallbackView.get_ding_id")
    def test_ding_sns_login_2(self, mock_get_ding_id):
        client = self.client
        ding_config = DingConfig.get_current()
        ding_config.__dict__.update(qr_app_id='qr_app_id', qr_app_secret='qr_app_secret', qr_app_valid=True)
        ding_config.save()
        accont_config = AccountConfig.get_current()
        accont_config.allow_ding_qr = True
        accont_config.save()
        mock_get_ding_id.side_effect = [{'ding_id': 'unregistered_dingid',\
            'openid': 'unknow_openid', 'unionid': 'unknowunionid'}]
        res = client.post(reverse('siteapi:ding_qr_callback'), data={'code':'CODE...........', 'state':'STATE'})
        expect = {'token': '', 'ding_id': 'unregistered_dingid'}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_ding_query_user(self, mock_check_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile':'18812341234'}]
        res = client.post(reverse('siteapi:ding_query_user'), data={'sms_token':'123132132131'})
        expect = {'exist':False}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_ding_query_user_2(self, mock_check_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile':'18812341234'}]
        res = client.post(reverse('siteapi:ding_query_user'), data={'sms_token': 'test_sms_token'})
        expect = {'exist':True}
        self.assertEqual(res.json(), expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_ding_bind(self, mock_check_sms_token):
        client = self.client
        user = User.objects.create(username='zhangsan', password='zhangsan', name='张三', mobile='18812341234')
        user.save()
        mock_check_sms_token.side_effect = [{'mobile':'18812341234'}]
        res = client.post(reverse('siteapi:ding_bind'), data={'sms_token':\
            'test_sms_token', 'ding_id':'ding_idding_id'})
        expect = ['token', 'uuid', 'user_id', 'username', 'name', 'email', 'mobile',\
            'employee_number', 'gender', 'ding_user', 'perms', 'avatar', 'roles',\
                'private_email', 'position', 'is_settled', 'is_manager', 'is_admin', 'is_extern_user', 'origin_verbose']
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_keys, expect)

    @mock.patch('siteapi.v1.serializers.ucenter.SMSClaimSerializer.check_sms_token')
    def test_ding_register_bind(self, mock_check_sms_token):
        client = self.client
        mock_check_sms_token.side_effect = [{'mobile':'18812341234'}]
        res = client.post(reverse('siteapi:ding_register_bind'),
                           data={
                               'username': 'username',
                               'password': 'password',
                               'sms_token': 'test_sms_token',
                               'ding_id':'test_ding_id'
                           })
        expect = ['uuid', 'user_id', 'username', 'name', 'email', 'mobile', 'employee_number',\
            'gender', 'perms', 'avatar', 'roles', 'private_email', 'position', 'is_settled',\
                'is_manager', 'is_admin', 'is_extern_user', 'origin_verbose', 'token']
        res_dict = res.json()
        res_keys = list(res_dict.keys())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res_keys, expect)
