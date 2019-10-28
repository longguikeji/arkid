# pylint: disable=missing-docstring

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import CompanyConfig, DingConfig, User, AccountConfig, AlipayConfig, WorkWechatConfig


class MetaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        employee = User.objects.create(username='employee')
        self.employee = self.login_as(employee)

    def test_meta(self):
        account_config = AccountConfig.get_current()
        account_config.allow_ding_qr = True
        account_config.allow_alipay_qr = True
        account_config.allow_work_wechat_qr = True
        account_config.save()
        company_config = CompanyConfig.get_current()
        company_config.fullname_cn = "demo"
        company_config.save()
        ding_config = DingConfig.get_current()
        ding_config.corp_id = "corp_id"
        ding_config.qr_app_id = 'qr_app_id'
        ding_config.qr_app_valid = True
        ding_config.save()
        alipay_config = AlipayConfig.get_current()
        alipay_config.app_id = 'test_app_id'
        alipay_config.qr_app_valid = True
        alipay_config.save()

        work_wechat_config = WorkWechatConfig.get_current()
        work_wechat_config.corp_id = 'test_corp_id'
        work_wechat_config.agent_id = 'test_agent_id'
        work_wechat_config.qr_app_valid = True
        work_wechat_config.save()

        res = self.anonymous.get(reverse('siteapi:meta'))
        expect = {
            'company_config': {
                'name_cn': '',
                'fullname_cn': 'demo',
                'name_en': '',
                'fullname_en': '',
                'icon': '',
                'address': '',
                'domain': '',
                'display_name': 'demo',
                'color': '',
            },
            'ding_config': {
                'corp_id': 'corp_id',
                'app_key': '',
                'qr_app_id': 'qr_app_id',
            },
            'account_config': {
                'support_email': False,
                'support_mobile': False,
                'support_email_register': False,
                'support_mobile_register': False,
                'support_ding_qr': True,
                'support_alipay_qr': True,
                'support_work_wechat_qr': True,
            },
            'alipay_config': {
                'app_id': 'test_app_id',
            },
            'work_wechat_config': {
                'corp_id': 'test_corp_id',
                'agent_id': 'test_agent_id'
            }
        }
        self.assertEqual(res.json(), expect)

    def test_meta_node(self):
        res = self.client.get(reverse('siteapi:meta_node'))
        expect = [{
            'name':
            '默认分类',
            'slug':
            'default',
            'node_uid':
            None,
            'nodes': [{
                'name': '部门',
                'node_uid': 'd_root',
                'node_subject': 'dept',
            }, {
                'name': '角色',
                'node_uid': 'g_role',
                'node_subject': 'role',
            }, {
                'name': '标签',
                'node_uid': 'g_label',
                'node_subject': 'label',
            }]
        }, {
            'name': '自定义分类',
            'slug': 'custom',
            'node_uid': 'g_intra',
            'nodes': []
        }]
        self.assertEqual(expect, res.json())

    def test_meta_perm(self):
        res = self.client.get(reverse('siteapi:meta_perm'))
        self.assertEqual(res.status_code, 200)

        res = self.employee.get(reverse('siteapi:meta_perm'))
        self.assertEqual(res.status_code, 403)
