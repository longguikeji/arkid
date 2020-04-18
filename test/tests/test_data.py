'''
测试数据库载入
'''
import os
from unittest import mock
from django.urls import reverse
from rest_framework.test import APIClient
from ...siteapi.v1.tests import TestCase
from ...oneid_meta.models import (
    AccountConfig,
    SMSConfig,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDBCase(TestCase):
    '''
    测试数据集是否载入及测试后数据是否改变
    '''
    def setUp(self):
        super().setUp()
        account_config = AccountConfig.get_current()
        account_config.allow_email = True
        account_config.allow_mobile = True
        account_config.allow_register = True
        account_config.save()

        mobile_config = SMSConfig.get_current()
        mobile_config.is_valid = True
        mobile_config.save()

        self.clear_sms_token_patcher = mock.patch('infrastructure.serializers.sms.SMSClaimSerializer.clear_sms_token')
        self.mock_clear_sms_token = self.clear_sms_token_patcher.start()
        self.mock_clear_sms_token.return_value = True

    def tearDown(self):
        self.clear_sms_token_patcher.stop()

    def test_login(self):    # pylint: disable=missing-function-docstring
        client = APIClient()
        res = client.post(reverse('siteapi:user_login'), data={'username': '13899990001', 'password': '1234'})
        self.assertEqual(res.status_code, 200)

    @mock.patch('siteapi.v1.serializers.ucenter.RegisterSMSClaimSerializer.check_sms_token')
    def test_register_by_mobile(self, mock_check_sms_token):
        '''
        测试注册
        '''
        client = APIClient()
        mock_check_sms_token.side_effect = [{'mobile': '18812341234'}]
        data = {
            'username': 'testregister',
            'password': 'pwd',
            'sms_token': 'mock',
        }
        res = client.post(reverse('siteapi:user_register'), data=data)
        self.assertEqual(res.status_code, 201)

    @mock.patch('siteapi.v1.serializers.ucenter.RegisterSMSClaimSerializer.check_sms_token')
    def test_register_by_mobile_2(self, mock_check_sms_token):
        '''
        测试注册
        '''
        client = APIClient()
        mock_check_sms_token.side_effect = [{'mobile': '13899990001'}]
        data = {
            'username': 'testregister',
            'password': 'pwd',
            'sms_token': 'mock',
        }
        res = client.post(reverse('siteapi:user_register'), data=data)
        self.assertEqual(res.status_code, 400)

    def test_data_users(self):
        '''
        测试数据集中的用户是否载入
        '''
        client = APIClient()
        res = client.post(reverse('siteapi:user_login'), data={'username': 'admin', 'password': 'admin'})
        token = res.json()['token']
        client.credentials(HTTP_AUTHORIZATION='token ' + token)
        res2 = client.get(reverse('siteapi:user_list'))
        usernames = [i['user']['username'] for i in res2.json()['results']]
        expect = [str(j) for j in range(13899990001, 13899990011)]
        self.assertEqual(usernames[:10], expect)
