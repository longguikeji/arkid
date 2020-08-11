# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from siteapi.v1.tests import TestCase
from oneid_meta.models import User, CustomField, SMSConfig, EmailConfig, I18NMobileConfig


# pylint: disable=too-many-lines
class ConfigTestCase(TestCase):
    def test_get_config(self):
        res = self.client.get(reverse('siteapi:config'))
        expect = {
            'company_config': {
                'name_cn': '',
                'fullname_cn': '',
                'name_en': '',
                'fullname_en': '',
                'icon': '',
                'address': '',
                'domain': '',
                'color': '',
            },
            'ding_config': {
                'app_key': '',
                'app_valid': False,
                'corp_id': '',
                'corp_valid': False,
                'qr_app_id': '',
                'qr_app_valid': False,
            },
            'account_config': {
                'allow_email': False,
                'allow_mobile': False,
                'allow_register': False,
                'allow_ding_qr': False,
                'allow_alipay_qr': False,
                'allow_qq_qr': False,
                'allow_work_wechat_qr': False,
                'allow_wechat_qr': False,
                'allow_github': False,
            },
            'sms_config': {
                'access_key': '',
                'signature': '',
                'template_code': '',
                'template_login': '',
                'template_register': '',
                'template_reset_pwd': '',
                'template_activate': '',
                'template_reset_mobile': '',
                'signature_i18n': '',
                'template_code_i18n': '',
                'template_login_i18n': '',
                'template_register_i18n': '',
                'template_reset_pwd_i18n': '',
                'template_activate_i18n': '',
                'template_reset_mobile_i18n': '',
                'vendor': 'aliyun',
                'is_valid': False,
            },
            'email_config': {
                'access_key': '',
                'host': '',
                'nickname': 'OneID',
                'port': 587,
                'is_valid': False,
            },
            'alipay_config': None,
            'qq_config': None,
            'work_wechat_config': None,
            'wechat_config': None,
            'password_config': {
                'is_active': True,
                'min_digit': 0,
                'min_length': 0,
                'min_letter': 0,
                'min_lower': 0,
                'min_special': 0,
                'min_upper': 0,
                'min_word': 0
            },
            'github_config': {
                'client_id': '',
                'client_valid': False
            },
        }
        self.assertEqual(res.json(), expect)

    @mock.patch('thirdparty_data_sdk.qq_sdk.qq_openid_sdk.QQInfoManager.check_config_valid')
    def test_update_qq_wechat_config(self, mock_check_config_valid):
        mock_check_config_valid.return_value = True
        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={
                                         'qq_config': {
                                             'app_id': 'test_app_id',
                                             'app_key': 'test_app_key',
                                             'redirect_uri': 'redirect_uri',
                                         },
                                     })
        expect = {
            'app_id': 'test_app_id',
            'qr_app_valid': True,
        }
        self.assertEqual(res.json()['qq_config'], expect)

    @mock.patch('thirdparty_data_sdk.work_wechat_sdk.user_info_manager.WorkWechatManager.check_valid')
    def test_update_work_wechat_config(self, mock_check_valid):
        mock_check_valid.return_value = True
        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={
                                         'work_wechat_config': {
                                             'corp_id': 'test_corp_id',
                                             'agent_id': 'test_agent_id',
                                             'secret': 'test_secret',
                                         },
                                     })
        expect = {
            'corp_id': 'test_corp_id',
            'agent_id': 'test_agent_id',
            'qr_app_valid': True,
        }
        self.assertEqual(res.json()['work_wechat_config'], expect)

    @mock.patch('thirdparty_data_sdk.wechat_sdk.wechat_user_info_manager.WechatUserInfoManager.check_valid')
    def test_update_wechat_config(self, mock_check_valid):
        mock_check_valid.return_value = True
        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={
                                         'wechat_config': {
                                             'appid': 'test_appid',
                                             'secret': 'test_secret',
                                         },
                                     })
        expect = {
            'appid': 'test_appid',
            'qr_app_valid': True,
        }
        self.assertEqual(res.json()['wechat_config'], expect)

    @mock.patch('thirdparty_data_sdk.alipay_api.alipay_user_id_sdk.check_valid')
    def test_update_alipay_config(self, mock_check_valid):
        mock_check_valid.return_value = True
        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={
                                         'alipay_config': {
                                             'app_id': 'test_app_id',
                                             'app_private_key': 'test_app_private_key',
                                             'alipay_public_key': 'test_alipay_public_key',
                                         },
                                     })
        expect = {'app_id': 'test_app_id', 'qr_app_valid': True}
        self.assertEqual(res.json()['alipay_config'], expect)

    @mock.patch('oneid_meta.models.config.SMSAliyunManager.send_auth_code')
    @mock.patch('oneid_meta.models.config.EmailManager.connect')
    @mock.patch('oneid_meta.models.config.DingConfig.check_valid')
    @mock.patch('siteapi.v1.serializers.config.DingConfigSerializer.validate_qr_app_config')
    @mock.patch('siteapi.v1.serializers.config.DingConfigSerializer.validate_app_config')
    @mock.patch('siteapi.v1.serializers.config.DingConfigSerializer.validate_corp_config')
    def test_update_config(self, mock_validate_corp_config, mock_validate_app_config,\
        mock_validate_qr_app_config, mock_check_valid, mock_connect,\
        mock_send_auth_code):
        mock_validate_corp_config.return_value = True
        mock_validate_app_config.return_value = False
        mock_validate_qr_app_config.return_value = True
        mock_check_valid.return_value = True
        mock_connect.return_value = True
        mock_send_auth_code.return_value = True
        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={
                                         'company_config': {
                                             'name_cn': 'demo',
                                             'fullname_cn': 'demo',
                                             'color': '006404',
                                         },
                                         'ding_config': {
                                             'app_key': 'app_key',
                                             'app_secret': 'pwd',
                                             'corp_id': 'corp_id',
                                             'corp_secret': 'pwd',
                                             'qr_app_id': 'qr_app_id',
                                             'qr_app_secret': 'qr_app_secret',
                                         },
                                         'account_config': {
                                             'allow_register': True,
                                             'allow_mobile': True,
                                             'allow_ding_qr': True,
                                             'allow_alipay_qr': False,
                                             'allow_qq_qr': True,
                                             'allow_work_wechat_qr': True
                                         },
                                         'sms_config': {
                                             'signature': 's',
                                             'signature_i18n': 's_i18n',
                                             'template_login': 'tl',
                                             'template_login_i18n': 'tl_i18n',
                                             'access_key': 'access_key',
                                             'access_secret': 'pwd',
                                         },
                                         'email_config': {
                                             'host': '12.12.12.12',
                                             'access_secret': 'pwd',
                                         },
                                         'password_config': {
                                             'is_active': True,
                                             'min_digit': 1,
                                             'min_length': 1,
                                             'min_letter': 1,
                                             'min_lower': 1,
                                             'min_special': 1,
                                             'min_upper': 1,
                                             'min_word': 1
                                         },
                                     })

        expect = {
            'company_config': {
                'name_cn': 'demo',
                'fullname_cn': 'demo',
                'name_en': '',
                'fullname_en': '',
                'icon': '',
                'address': '',
                'domain': '',
                'color': '006404',
            },
            'ding_config': {
                'app_key': '',
                'app_valid': False,
                'corp_id': 'corp_id',
                'corp_valid': True,
                'qr_app_id': 'qr_app_id',
                'qr_app_valid': True,
            },
            'account_config': {
                'allow_email': False,
                'allow_mobile': True,
                'allow_register': True,
                'allow_ding_qr': True,
                'allow_alipay_qr': False,
                'allow_qq_qr': True,
                'allow_work_wechat_qr': True,
                'allow_wechat_qr': False,
                'allow_github': False,
            },
            'sms_config': {
                'access_key': 'access_key',
                'signature': 's',
                'template_code': '',
                'template_login': 'tl',
                'template_register': '',
                'template_reset_pwd': '',
                'template_activate': '',
                'template_reset_mobile': '',
                'signature_i18n': 's_i18n',
                'template_code_i18n': '',
                'template_login_i18n': 'tl_i18n',
                'template_register_i18n': '',
                'template_reset_pwd_i18n': '',
                'template_activate_i18n': '',
                'template_reset_mobile_i18n': '',
                'vendor': 'aliyun',
                'is_valid': True,
            },
            'email_config': {
                'access_key': '',
                'host': '12.12.12.12',
                'nickname': 'OneID',
                'port': 587,
                'is_valid': True,
            },
            'alipay_config': None,
            'work_wechat_config': None,
            'wechat_config': None,
            'qq_config': None,
            'password_config': {
                'is_active': True,
                'min_digit': 1,
                'min_length': 1,
                'min_letter': 1,
                'min_lower': 1,
                'min_special': 1,
                'min_upper': 1,
                'min_word': 1
            },
            'github_config': {
                'client_id': '',
                'client_valid': False
            }
        }

        self.assertEqual(res.json(), expect)
        self.assertEqual(EmailConfig.get_current().access_secret, 'pwd')
        self.assertEqual(SMSConfig.get_current().access_secret, 'pwd')

        res = self.client.json_patch(reverse('siteapi:config'),
                                     data={'email_config': {
                                         'host': '12.12.12.13',
                                         'access_secret': '',
                                     }})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email_config']['host'], "12.12.12.13")

        res = self.client.json_patch(reverse('siteapi:config'), data={'company_config':\
            {'name_cn': "abc", 'icon': "", 'color': "zzzzzz"}})
        expect = {'company_config': {'non_field_errors': ["color invalid"]}}
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(reverse('siteapi:config'), data={'company_config':\
            {'name_cn': "abc", 'icon': "", 'color': "AAFEAE"}})
        self.assertEqual(res.status_code, HTTP_200_OK)

    def test_update_config_valid(self):
        with mock.patch('oneid_meta.models.config.EmailManager.connect') as mock_connect:
            mock_connect.return_value = True
            self.client.json_patch(reverse('siteapi:config'),
                                   data={
                                       'account_config': {
                                           'allow_register': True,
                                           'allow_email': True,
                                       },
                                       'email_config': {
                                           'nickname': '.'
                                       }
                                   })
        res = self.anonymous.get(reverse('siteapi:meta'))
        expect = {
            'support_email': True,
            'support_mobile': False,
            'support_email_register': True,
            'support_mobile_register': False,
            'support_ding_qr': False,
            'support_alipay_qr': False,
            'support_qq_qr': False,
            'support_work_wechat_qr': False,
            'support_wechat_qr': False,
        }
        self.assertEqual(expect, res.json()['account_config'])

        with mock.patch('oneid_meta.models.config.SMSConfig.check_valid') as mock_check_valid:
            mock_check_valid.return_value = True
            self.client.json_patch(reverse('siteapi:config'),
                                   data={
                                       'account_config': {
                                           'allow_register': False,
                                           'allow_mobile': True,
                                       },
                                       'sms_config': {
                                           'signature': '.'
                                       }
                                   })
        res = self.anonymous.get(reverse('siteapi:meta'))
        expect = {
            'support_ding_qr': False,
            'support_email': True,
            'support_mobile': True,
            'support_email_register': False,
            'support_mobile_register': False,
            'support_alipay_qr': False,
            'support_qq_qr': False,
            'support_work_wechat_qr': False,
            'support_wechat_qr': False,
        }
        self.assertEqual(expect, res.json()['account_config'])


class ConfigAlterAdminTestCase(TestCase):
    @mock.patch("infrastructure.serializers.sms.SMSClaimSerializer.check_sms_token")
    def test_alter_admin(self, mock_sms_token):
        mock_sms_token.side_effect = [
            {
                'mobile': '18812340001'
            },
            {
                'mobile': '18812340002'
            },
        ]
        old_admin = User.create_user('old_admin', 'old_admin')
        old_admin.is_boss = True
        old_admin.mobile = '18812340001'
        old_admin.save()

        new_admin = User.create_user('new_admin', '')
        new_admin.mobile = '18812340002'
        new_admin.save()

        res = self.client.json_patch(reverse('siteapi:alter_admin'),
                                     data={
                                         'old_admin_sms_token': 'test',
                                         'new_admin_sms_token': 'test'
                                     })
        self.assertEqual(res.status_code, 200)

        old_admin = User.objects.get(username='old_admin')
        new_admin = User.objects.get(username='new_admin')
        self.assertFalse(old_admin.is_boss)
        self.assertTrue(new_admin.is_boss)


class ConfigCustomFieldTestCase(TestCase):
    def test_custom_field(self):
        res = self.client.json_post(reverse("siteapi:custom_field_list", args=('user', )), data={'name': '忌口'}).json()
        uuid = res['uuid']
        expect = {'uuid': uuid, 'name': '忌口', 'subject': 'user', 'schema': {'type': 'string'}, 'is_visible': True}
        self.assertEqual(res, expect)

        res = self.client.get(reverse("siteapi:custom_field_list", args=('user', )))
        expect = [{'uuid': uuid, 'name': '忌口', 'subject': 'user', 'schema': {'type': 'string'}, 'is_visible': True}]
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(reverse("siteapi:custom_field_detail", args=('user', uuid)), data={'name': '爱好'})
        expect = {'uuid': uuid, 'name': '爱好', 'subject': 'user', 'schema': {'type': 'string'}, 'is_visible': True}
        self.assertEqual(res.json(), expect)

        res = self.client.delete(reverse("siteapi:custom_field_detail", args=('user', uuid)))
        self.assertEqual(res.status_code, 204)
        self.assertEqual(CustomField.valid_objects.count(), 0)

    def test_create_extern_user_custom_field(self):    # pylint: disable=invalid-name
        res = self.client.json_post(reverse("siteapi:custom_field_list", args=('extern_user', )),\
            data={'name': '忌口'}).json()
        res.pop('uuid')
        expect = {'name': '忌口', 'subject': 'extern_user', 'schema': {'type': 'string'}, 'is_visible': True}
        self.assertEqual(res, expect)
        res = self.client.get(reverse("siteapi:custom_field_list", args=('extern_user', )))
        self.assertEqual(len(res.json()), 1)

    def test_custom_field_active(self):
        res = self.client.json_post(reverse("siteapi:custom_field_list", args=('user', )), data={'name': '忌口'}).json()
        uuid = res['uuid']
        self.assertTrue(res['is_visible'])

        res = self.client.json_patch(reverse('siteapi:custom_field_detail', args=(
            'user',
            uuid,
        )),
                                     data={'is_visible': False})
        self.assertFalse(res.json()['is_visible'])


class ConfigNativeFieldTestCase(TestCase):
    def test_native_field(self):
        res = self.client.json_post(reverse('siteapi:native_field_list', args=('user', )), data={'name': '职位'})
        self.assertEqual(res.status_code, 405)
        res = self.client.get(reverse('siteapi:native_field_list', args=('user', )))
        items = res.json()
        keys = [item['key'] for item in res.json()]
        expect = ['name', 'employee_number', 'gender', 'mobile', 'email', 'depts']
        self.assertEqual(keys, expect)

        # mobile: editable
        mobile_uuid = ''
        for item in items:
            if item['key'] == 'mobile':
                mobile_uuid = item['uuid']

        res = self.client.json_patch(reverse('siteapi:native_field_detail', args=('user', mobile_uuid)),
                                     data={'is_visible': 'False'})
        self.assertFalse(res.json()['is_visible'])

        # email: not editable
        email_uuid = ''
        for item in items:
            if item['key'] == 'email':
                email_uuid = item['uuid']
        res = self.client.json_patch(reverse('siteapi:native_field_detail', args=('user', email_uuid)),
                                     data={'is_visible': False})
        self.assertEqual(res.status_code, 400)


class ConfigStorageTestCase(TestCase):
    def test_storage_field(self):
        res = self.client.get(reverse('siteapi:storage_config'))
        expect = {
            'method': 'local',
            'minio_config': {
                'end_point': '',
                'access_key': '',
                'secret_key': '',
                'secure': True,
                'location': '',
                'bucket': '',
            },
        }
        self.assertEqual(res.json(), expect)

        method = 'minio'
        minio_config = {
            'end_point': 'localhost:12345',
            'access_key': '123',
            'secret_key': '123',
            'secure': False,
            'location': 'us-east-4',
            'bucket': 'arkid',
        }

        res = self.client.json_patch(reverse('siteapi:storage_config'),
                                     data={
                                         'method': method,
                                         'minio_config': minio_config,
                                     })
        expect = {
            'method': 'minio',
            'minio_config': {
                'end_point': 'localhost:12345',
                'access_key': '123',
                'secret_key': '123',
                'secure': False,
                'location': 'us-east-4',
                'bucket': 'arkid',
            }
        }
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:storage_config'))
        expect = {
            'method': 'minio',
            'minio_config': {
                'end_point': 'localhost:12345',
                'access_key': '123',
                'secret_key': '123',
                'secure': False,
                'location': 'us-east-4',
                'bucket': 'arkid',
            }
        }
        self.assertEqual(res.json(), expect)


class ConfigI18NMobileTestCase(TestCase):
    """测试国际手机号接入配置"""
    def test_get_i18n_mobile_config(self):
        """测试查询国际手机号接入配置"""
        config = {
            'uuid': None,
            'state': 'China',
            'state_code': '86',
            'number_length': 11,
            'start_digital': [1],
            'is_active': True
        }
        res = self.client.get(reverse("siteapi:i18n_mobile_config_list")).json()
        self.assertEqual(1, len(res))
        config.update(uuid=res[0]['uuid'])
        self.assertEqual(config, res[0])

    def test_create_i18n_mobile_config(self):
        """测试创建国际手机号接入配置"""
        config = {
            'state': 'HongKong',
            'state_code': '852',
            'number_length': 8,
            'start_digital': [5, 6, 9],
        }
        expect = {
            'uuid': None,
            'state': 'HongKong',
            'state_code': '852',
            'number_length': 8,
            'start_digital': [5, 6, 9],
            'is_active': True
        }
        res = self.client.json_post(reverse("siteapi:i18n_mobile_config_list"), data=config).json()
        expect.update(uuid=res['uuid'])
        self.assertEqual(expect, res)

    def test_delete_i18n_mobile_config(self):
        """测试删除国际手机号接入配置"""
        config = I18NMobileConfig.objects.create(state='HongKong', state_code='852', number_length=8)
        res = self.client.delete(reverse("siteapi:i18n_mobile_config_detail", args=(config.uuid, )))
        self.assertEqual(204, res.status_code)

    def test_update_i18n_mobile_config(self):
        """测试更新国际手机号接入配置"""
        config = I18NMobileConfig.objects.create(state='HongKong', state_code='852', number_length=8)
        expect = {
            'uuid': config.uuid.hex,
            'state': 'HongKong',
            'state_code': '852',
            'number_length': 8,
            'start_digital': [],
            'is_active': False
        }
        # pylint: disable=line-too-long
        res = self.client.json_patch(reverse("siteapi:i18n_mobile_config_detail", args=(config.uuid, )),
                                     data={
                                         'is_active': False
                                     }).json()
        self.assertEqual(expect, res)
