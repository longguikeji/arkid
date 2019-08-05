# pylint: disable=missing-docstring

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import CompanyConfig, DingConfig, User


class MetaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        employee = User.objects.create(username='employee')
        self.employee = self.login_as(employee)

    def test_meta(self):
        company_config = CompanyConfig.get_current()
        company_config.fullname_cn = "demo"
        company_config.save()
        ding_config = DingConfig.get_current()
        ding_config.corp_id = "corp_id"
        ding_config.save()

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
            },
            'account_config': {
                'support_email': False,
                'support_mobile': False,
                'support_email_register': False,
                'support_mobile_register': False,
            },
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
