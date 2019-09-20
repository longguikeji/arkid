'''
tests for api about app
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    APP,
    OAuthAPP,
    Perm,
    User,
    UserPerm,
    Dept,
    Group,
    GroupMember,
    ManagerGroup,
)

MAX_APP_ID = 2

APP_1 = {'name': 'demo'}

APP_1_EXCEPT = {
    'app_id': MAX_APP_ID + 1,
    'uid': 'demo',
    'name': 'demo',
    'logo': '',
    'index': '',
    'remark': '',
    'oauth_app': None,
    'http_app': None,
    'ldap_app': None,
    'allow_any_user': False,
    'auth_protocols': [],
}

APP_2 = {
    'uid': 'test_uid',
    'name': 'test_name',
    'remark': 'test_remark',
    'allow_any_user': True,
    'oauth_app': {
        'redirect_uris': 'http://localhost/callback'
    },
    'ldap_app': {},
    'http_app': {},
}

APP_2_EXCEPT = {
    'app_id': MAX_APP_ID + 2,
    'uid': 'test_uid',
    'name': 'test_name',
    'logo': '',
    'index': '',
    'remark': 'test_remark',
    'allow_any_user': True,
    'oauth_app': {
        'redirect_uris': 'http://localhost/callback',
        'client_type': 'confidential',
        'authorization_grant_type': 'authorization-code',
        'more_detail': [],
    },
    'ldap_app': {
        'more_detail': []
    },
    'http_app': {
        'more_detail': []
    },
    'auth_protocols': ['OAuth 2.0', 'LDAP', 'HTTP'],
}


class APPTestCase(TestCase):
    def setUp(self):
        super().setUp()
        employee = User.create_user('employee', 'employee')
        self.employee = self.login_as(employee)
        self._employee = employee

        manager = User.create_user('manager', 'manager')
        self.manager = self.login_as(manager)
        self._manager = manager
        group = Group.objects.create(name='test')
        ManagerGroup.objects.create(group=group, scope_subject=2, apps=['app', 'demo'])
        GroupMember.objects.create(owner=group, user=User.objects.get(username='manager'))

    @mock.patch('oneid_meta.models.app.LDAPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oneid_meta.models.app.HTTPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oauth2_provider.models.Application.more_detail', new_callable=mock.PropertyMock)
    def test_create_app(
            self,
            mock_oauth_info,
            mock_http_info,
            mock_ldap_info,
    ):
        mock_oauth_info.return_value = []
        mock_http_info.return_value = []
        mock_ldap_info.return_value = []

        res = self.client.json_post(reverse('siteapi:app_list'), data=APP_1)
        self.assertEqual(res.json(), APP_1_EXCEPT)

        res = self.client.json_post(reverse('siteapi:app_list'), data=APP_2)

        res = res.json()
        self.assertIn('client_id', res['oauth_app'])
        self.assertIn('client_secret', res['oauth_app'])
        del res['oauth_app']['client_id']
        del res['oauth_app']['client_secret']
        self.assertEqual(res, APP_2_EXCEPT)

        res = self.client.json_post(reverse('siteapi:app_list'),
                                    data={
                                        'uid': 'test_uid',
                                        'name': 'test_name',
                                        'remark': 'test_remark',
                                        'oauth_app': {
                                            'redirect_uris': 'http://localhost/callback',
                                            'client_type': 'out_of_choices'
                                        },
                                        'ldap_app': {},
                                        'http_app': {},
                                    })
        expect_error = {
            'oauth_app': {
                'client_type': ['"out_of_choices" is not a valid choice.']
            },
            'uid': ['this value has be used'],
        }
        self.assertEqual(res.json(), expect_error)
        self.assertEqual(res.status_code, 400)

        self.assertTrue(Perm.valid_objects.filter(uid='app_test_uid_access').exists())

    @mock.patch('oneid_meta.models.app.LDAPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oneid_meta.models.app.HTTPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oauth2_provider.models.Application.more_detail', new_callable=mock.PropertyMock)
    def test_employee_create_app(
            self,
            mock_oauth_info,
            mock_http_info,
            mock_ldap_info,
    ):
        mock_oauth_info.return_value = []
        mock_http_info.return_value = []
        mock_ldap_info.return_value = []

        res = self.employee.json_post(reverse('siteapi:app_list'), data={'name': 'testname'})
        self.assertEqual(res.status_code, 403)
        perm, _ = Perm.objects.get_or_create(subject='system', scope='app', action='create')
        user_perm = UserPerm.get(self._employee, perm)
        user_perm.permit()
        res = self.employee.json_post(reverse('siteapi:app_list'), data={'name': 'testname'})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(list(self._employee.manager_groups)), 1)
        manager_group = list(self._employee.manager_groups)[0]
        self.assertEqual(manager_group.apps, ['testname'])
        self.assertEqual(manager_group.group.users, [self._employee])

    @mock.patch('oneid_meta.models.app.LDAPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oneid_meta.models.app.HTTPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oauth2_provider.models.Application.more_detail', new_callable=mock.PropertyMock)
    def test_update_app(
            self,
            mock_oauth_info,
            mock_http_info,
            mock_ldap_info,
    ):
        mock_oauth_info.return_value = []
        mock_http_info.return_value = []
        mock_ldap_info.return_value = []

        self.client.json_post(reverse('siteapi:app_list'), data=APP_1)
        res = self.client.json_patch(reverse('siteapi:app_detail', args=(APP_1_EXCEPT['uid'], )),
                                     data={
                                         'remark': 'changed',
                                         'oauth_app': {
                                             'redirect_uris': 'http://localhost/callback',
                                         },
                                         'index': 'index',
                                         'logo': 'logo',
                                         'ldap_app': {},
                                     }).json()
        self.assertIn('client_secret', res['oauth_app'])
        self.assertIn('client_id', res['oauth_app'])
        self.assertIn('ldap_app', res)
        del res['oauth_app']['client_secret']
        del res['oauth_app']['client_id']
        del res['ldap_app']
        expect = {
            'app_id': MAX_APP_ID + 1,
            'allow_any_user': False,
            'uid': 'demo',
            'name': 'demo',
            'logo': 'logo',
            'index': 'index',
            'remark': 'changed',
            'oauth_app': {
                'redirect_uris': 'http://localhost/callback',
                'client_type': 'confidential',
                'authorization_grant_type': 'authorization-code',
                'more_detail': [],
            },
            'http_app': None,
            'auth_protocols': ['OAuth 2.0', 'LDAP'],
        }
        self.assertEqual(res, expect)
        self.assertTrue(OAuthAPP.objects.filter(app__uid=APP_1_EXCEPT['uid']).exists())

        res = self.client.json_patch(reverse('siteapi:app_detail', args=(APP_1_EXCEPT['uid'], )),
                                     data={
                                         'remark': 'changed',
                                         'oauth_app': None,
                                         'ldap_app': None,
                                         'index': 'index',
                                         'logo': 'logo',
                                     })
        self.assertIsNone(res.json()['oauth_app'])
        self.assertIsNone(res.json()['ldap_app'])
        self.assertEqual(res.json()['auth_protocols'], [])

    def test_update_app_protected(self):

        self.client.json_post(reverse('siteapi:app_list'), data=APP_2)
        app2 = APP.valid_objects.get(uid='test_uid')
        app2.editable = False
        app2.save()
        res = self.client.json_patch(reverse('siteapi:app_detail', args=('test_uid', )), data={'remark': 'new'})
        self.assertEqual(res.status_code, 405)

    def test_delete_app(self):
        self.client.json_post(reverse('siteapi:app_list'), data=APP_1)
        self.assertTrue(APP.valid_objects.filter(uid=APP_1_EXCEPT['uid']).exists())
        self.assertTrue(Perm.valid_objects.filter(uid='app_demo_access').exists())

        res = self.client.delete(reverse('siteapi:app_detail', args=(APP_1_EXCEPT['uid'], )))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(APP.valid_objects.filter(uid=APP_1_EXCEPT['uid']).exists())
        self.assertTrue(APP.objects.filter(uid=APP_1_EXCEPT['uid'], is_del=True).exists())
        self.assertFalse(OAuthAPP.objects.filter(app__uid=APP_1_EXCEPT['uid']).exists())
        self.assertFalse(Perm.objects.filter(uid='app_demo_access').exists())

        self.client.json_post(reverse('siteapi:app_list'), data=APP_2)
        app2 = APP.valid_objects.get(uid='test_uid')
        app2.editable = False
        app2.save()
        res = self.client.delete(reverse('siteapi:app_detail', args=('test_uid', )))
        self.assertEqual(res.status_code, 405)

    def test_app_list(self):
        self.client.json_post(reverse('siteapi:app_list'), data=APP_1)
        self.client.json_post(reverse('siteapi:app_list'), data=APP_2)
        res = self.client.get(reverse('siteapi:app_list'))
        expect = {    # pylint: disable=unused-variable
            'count':
            2,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'app_id': 1,
                'uid': 'demo',
                'name': 'demo',
                'logo': '',
                'index': '',
                'remark': '',
                'oauth_app': None
            }, {
                'app_id': 2,
                'uid': 'test_uid',
                'name': 'test_name',
                'remark': 'test_remark',
                'oauth_app': {
                    'client_id': '02DnhbcRvC0ogKC41lxbTpF4mK0gFPRhWx42kCvU',
                    'client_secret': 'KHzsR85aIt1oQu0Y3OdruVvCiT5z5FhqPY...EGw5PRsWz3TK2FOnbAIyPuS3P7ke',
                    'redirect_uris': 'http://localhost/callback',
                    'client_type': 'confidential',
                    'authorization_grant_type': 'authorization-code'
                },
                'access_perm': {
                    'perm_id': 4,
                    'uid': 'app_test_uid_access',
                    'name': '访问test_name',
                    'remark': '',
                    'scope': 'test_uid',
                    'action': 'access',
                    'subject': 'app',
                    'permit_owners': {
                        'count': 0,
                        'results': [],
                        'has_more': False
                    },
                    'reject_owners': {
                        'count': 0,
                        'results': [],
                        'has_more': False
                    },
                },
                'auth_protocols': ['OAuth 2.0'],
            }]
        }    # only for display
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], MAX_APP_ID + 2 - 1)    # 不包括OneID
        self.assertIn('access_perm', res.json()['results'][0])

        res = self.client.get(reverse('siteapi:app_list'), data={'page_size': 1, 'page': 2})
        self.assertEqual(res.status_code, 200)

    def test_ucenter_app_list(self):
        self.client.json_post(reverse('siteapi:app_list'), data=APP_1)

        res = self.employee.get(reverse('siteapi:ucenter_app_list'))
        self.assertEqual(res.json()['count'], 0)
        perm = Perm.objects.get(uid='app_demo_access')
        user_perm = UserPerm.get(User.objects.get(username='employee'), perm)
        user_perm.permit()
        res = self.employee.get(reverse('siteapi:ucenter_app_list'))
        expect = ['demo']
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])

    def test_app_perm(self):
        User.objects.get(username='employee')
        APP.objects.create(uid='app', name='app')
        res = self.employee.get(reverse('siteapi:app_list'))
        self.assertEqual(res.status_code, 403)
        res = self.manager.get(reverse('siteapi:app_list'))
        self.assertEqual(res.status_code, 200)

        res = self.employee.json_patch(reverse('siteapi:app_detail', args=('app', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 403)

        res = self.manager.json_patch(reverse('siteapi:app_detail', args=('app', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 200)

    def test_app_list_with(self):
        self.client.json_post(reverse('siteapi:app_list'), data=APP_1)

        res = self.employee.get(reverse('siteapi:app_list'), data={'node_uid': 'd_root', 'owner_access': True})
        self.assertEqual(res.status_code, 403)

        res = self.manager.get(reverse('siteapi:app_list'), data={'node_uid': 'd_root', 'owner_access': True})
        self.assertEqual(0, res.json()['count'])

        dept = Dept.objects.get(uid='root')
        perm = Perm.objects.get(uid='app_demo_access')
        owner_perm = dept.owner_perm_cls.get(dept, perm)
        owner_perm.permit()

        res = self.manager.get(reverse('siteapi:app_list'), data={'node_uid': 'd_root', 'owner_access': True})
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'app_id': MAX_APP_ID + 1,
                'uid': 'demo',
                'name': 'demo',
                'logo': '',
                'remark': '',
                'index': '',
                'oauth_app': None,
                'ldap_app': None,
                'http_app': None,
                'allow_any_user': False,
                'access_perm': {
                    'perm_id': 3,
                    'uid': 'app_demo_access',
                    'name': '访问demo',
                    'remark': '',
                    'scope': 'demo',
                    'action': 'access',
                    'subject': 'app',
                    'permit_owners': {
                        'count': 1,
                        'results': [{
                            'uid': 'd_root',
                            'name': 'root',
                            'subject': 'dept'
                        }],
                        'has_more': False
                    },
                    'reject_owners': {
                        'count': 0,
                        'results': [],
                        'has_more': False
                    }
                },
                'auth_protocols': [],
                'access_result': {
                    'node_uid': 'd_root',
                    'user_uid': '',
                    'value': True
                }
            }]
        }
        self.assertEqual(expect, res.json())

    def test_app_register_oauth(self):
        uid = 'mock-1'
        res = self.client.json_post(reverse('siteapi:app_register_oauth', args=(uid, )),
                                    data={'redirect_uris': 'http://test.com/oauth/callback'})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['redirect_uris'], 'http://test.com/oauth/callback')
        self.assertEqual(APP.objects.get(uid=uid).index, 'http://test.com')

        res = self.client.json_post(reverse('siteapi:app_register_oauth', args=(uid, )),
                                    data={'redirect_uris': 'http://new.test.com/oauth/callback'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['redirect_uris'], 'http://new.test.com/oauth/callback')
        self.assertEqual(APP.objects.get(uid=uid).index, 'http://new.test.com')
