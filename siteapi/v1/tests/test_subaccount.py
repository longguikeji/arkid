'''
tests for sub account
'''
# pylint: disable=missing-docstring

from django.urls import reverse

from oneid_meta.models import User, APP, Perm, UserPerm, GroupMember
from siteapi.v1.views.org import validity_check
from siteapi.v1.tests import TestCase


class AdminSubAccountPermTestCase(TestCase):
    '''
    测试管理员管理应用子账号
    '''
    def setUp(self):
        super().setUp()

        self.org = validity_check(
            self.client.json_post(reverse('siteapi:org_list'), data={
                'name': 'org'
            }).json()['oid'])
        self.app = APP.objects.create(name='lg', uid='lg', owner=self.org)

    def create_sub_account_perm(self):
        res = self.client.json_post(reverse("siteapi:perm_list"),
                                    data={
                                        "scope": "lg",
                                        "sub_account": {
                                            "domain": "www.longguikeji.com",
                                            "username": "admin",
                                            "password": "admin",
                                        }
                                    })
        return res

    def create_inner_perm(self):
        res = self.client.json_post(reverse("siteapi:perm_list"), data={
            "scope": "lg",
            "name": "访问后台",
        })
        return res

    def test_create_sub_account_perm(self):
        res = self.create_sub_account_perm()
        self.assertEqual(res.status_code, 201)
        sub_account_expect = {
            "domain": "www.longguikeji.com",
            "username": "admin",
            "password": "admin",
        }
        sub_account_test = res.json()['sub_account']
        sub_account_test.pop('uuid')
        self.assertEqual(res.json()['sub_account'], sub_account_expect)

    def test_patch_sub_account_perm(self):
        res = self.create_sub_account_perm()
        perm_uid = res.json()['uid']

        res = self.client.json_patch(reverse("siteapi:perm_detail", args=(perm_uid, )),
                                     data={'sub_account': {
                                         "password": "new_password",
                                         "username": "new_account"
                                     }})
        sub_account_expect = {
            "domain": "www.longguikeji.com",
            "username": "new_account",
            "password": "new_password",
        }
        sub_account_test = res.json()['sub_account']
        sub_account_test.pop('uuid')
        self.assertEqual(res.json()['sub_account'], sub_account_expect)
        self.assertEqual(res.json()['name'], '以 "new_account" 身份访问 lg')

    def test_get_perm_list(self):
        self.create_sub_account_perm()
        self.create_inner_perm()

        access_perm_res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'lg', 'action': 'access'})
        self.assertEqual(access_perm_res.json()['count'], 1)
        self.assertEqual([item['name'] for item in access_perm_res.json()['results']], ['以 "admin" 身份访问 lg'])
        self.assertIn('sub_account', access_perm_res.json()['results'][0])

        access_perm_res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'lg', 'action_except': 'access'})
        self.assertEqual(access_perm_res.json()['count'], 1)
        self.assertEqual([item['name'] for item in access_perm_res.json()['results']], ['访问后台'])

    def test_ucenter_sub_account(self):
        res = self.create_sub_account_perm()
        perm = Perm.objects.get(uid=res.json()['uid'])
        employee = User.create_user(username='employee', password='employee')
        GroupMember.valid_objects.create(user=employee, owner=self.org.direct)

        client = self.login_as(employee)
        res = client.get(reverse('siteapi:ucenter_sub_account_list'))
        self.assertEqual(res.json()['count'], 0)
        res = client.get(reverse('siteapi:ucenter_app_list'))
        self.assertEqual(res.json()['count'], 0)

        self.client.json_patch(reverse('siteapi:org_user_list', args=(self.org.oid, )),
                               data={
                                   'usernames': ['employee'],
                                   "subject": "add"
                               })
        UserPerm.objects.create(owner=employee, perm=perm).permit()
        res = client.get(reverse('siteapi:ucenter_sub_account_list'))
        self.assertEqual(res.json()['count'], 1)
        sub_account_test = res.json()['results'][0]
        sub_account_test.pop('uuid')
        sub_account_except = {'domain': 'www.longguikeji.com', 'username': 'admin', 'password': 'admin'}
        self.assertEqual(sub_account_except, sub_account_test)

        res = client.get(reverse('siteapi:ucenter_app_list'))
        self.assertEqual(res.json()['count'], 1)
        app_test = [item['uid'] for item in res.json()['results']]
        app_expect = ['lg']
        self.assertEqual(app_expect, app_test)

        res = client.get(reverse('siteapi:ucenter_sub_account_list'), data={'domain': 'www.longguikeji.com'})
        self.assertEqual(res.json()['count'], 1)

        res = client.get(reverse('siteapi:ucenter_sub_account_list'), data={'domain': 'arkid.longguikeji.com'})
        self.assertEqual(res.json()['count'], 0)
