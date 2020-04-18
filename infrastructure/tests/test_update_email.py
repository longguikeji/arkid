'''
测试邮箱链接激活
'''
from unittest import mock

from django.urls import reverse

from ...siteapi.v1.tests import TestCase
from ...oneid_meta.models import (
    User,
    AccountConfig,
    EmailConfig,
)

MAX_APP_ID = 2

VISIABLE_FIELDS = ['name', 'email', 'depts', 'mobile', 'employee_number', 'gender']


class EmailTestCase(TestCase):
    '''
    更新邮箱测试
    '''
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

        self.clear_email_token_patcher = mock.patch(
            'infrastructure.serializers.email.EmailClaimSerializer.clear_email_token')
        self.mock_clear_email_token = self.clear_email_token_patcher.start()
        self.mock_clear_email_token.return_value = True

    def tearDown(self):
        self.clear_email_token_patcher.stop()

    @mock.patch('oneid.utils.redis_conn.hgetall')
    def test_email_link(self, mock_hgetall):
        '''
        更新邮箱测试
        '''
        mock_hgetall.return_value = {"email": "a@b.com", "username": "test", "name": ""}
        user = User.create_user(username='test', password='test')
        user.mobile = '18812341234'
        user.email = '12@34.com'
        user.save()

        client = self.login_as(user)

        url = reverse('infra:email', args=('update_email', ))
        update_email_response = client.get(url, data={'email_token': 'test_email_token'})
        self.assertEqual(update_email_response.status_code, 200)
