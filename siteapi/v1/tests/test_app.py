'''
tests for api about app
'''
# pylint: disable=missing-docstring, too-many-lines, attribute-defined-outside-init
import os
from unittest import mock
from django.urls import reverse
from djangosaml2idp.scripts.idpinit import run

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

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
    'saml_app': None,
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
    'saml_app': None,
    'auth_protocols': ['OAuth 2.0', 'LDAP', 'HTTP'],
}

APP_3 = {
    'uid': 'test_app_uid',
    'name': 'test_app_name',
    'index': 'http://localhost:8087',
    'auth_protocols': ["SAML2"],
    'remark': 'test_remark',
    'allow_any_user': True,
    'oauth_app': {},
    'ldap_app': {},
    'http_app': {},
    'saml_app': {
        'entity_id': 'http://localhost/sp/saml',
        'acs': 'http://localhost:8087/acs/post',
        'sls': 'http://localhost:8087/sls/post',
        'cert': '-----BEGIN CERTIFICATE-----\n\
MIIC8jCCAlugAwIBAgIJAJHg2V5J31I8MA0GCSqGSIb3DQEBBQUAMFoxCzAJBgNV\
BAYTAlNFMQ0wCwYDVQQHEwRVbWVhMRgwFgYDVQQKEw9VbWVhIFVuaXZlcnNpdHkx\
EDAOBgNVBAsTB0lUIFVuaXQxEDAOBgNVBAMTB1Rlc3QgU1AwHhcNMDkxMDI2MTMz\
MTE1WhcNMTAxMDI2MTMzMTE1WjBaMQswCQYDVQQGEwJTRTENMAsGA1UEBxMEVW1l\
YTEYMBYGA1UEChMPVW1lYSBVbml2ZXJzaXR5MRAwDgYDVQQLEwdJVCBVbml0MRAw\
DgYDVQQDEwdUZXN0IFNQMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkJWP7\
bwOxtH+E15VTaulNzVQ/0cSbM5G7abqeqSNSs0l0veHr6/ROgW96ZeQ57fzVy2MC\
FiQRw2fzBs0n7leEmDJyVVtBTavYlhAVXDNa3stgvh43qCfLx+clUlOvtnsoMiiR\
mo7qf0BoPKTj7c0uLKpDpEbAHQT4OF1HRYVxMwIDAQABo4G/MIG8MB0GA1UdDgQW\
BBQ7RgbMJFDGRBu9o3tDQDuSoBy7JjCBjAYDVR0jBIGEMIGBgBQ7RgbMJFDGRBu9\
o3tDQDuSoBy7JqFepFwwWjELMAkGA1UEBhMCU0UxDTALBgNVBAcTBFVtZWExGDAW\
BgNVBAoTD1VtZWEgVW5pdmVyc2l0eTEQMA4GA1UECxMHSVQgVW5pdDEQMA4GA1UE\
AxMHVGVzdCBTUIIJAJHg2V5J31I8MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF\
BQADgYEAMuRwwXRnsiyWzmRikpwinnhTmbooKm5TINPE7A7gSQ710RxioQePPhZO\
zkM27NnHTrCe2rBVg0EGz7QTd1JIwLPvgoj4VTi/fSha/tXrYUaqc9AqU1kWI4WN\
+vffBGQ09mo+6CffuFTZYeOhzP/2stAPwCTU4kxEoiy0KpZMANI=\n\
-----END CERTIFICATE-----',
        'xmldata': '',
    },
}


class APPTestCase(TestCase):
    def setUp(self):
        run()
        super().setUp()

        org = self.client.json_post(reverse('siteapi:org_create'), data={'name': 'org1'}).json()
        self.org = org['oid']
        self.org_data = org

        employee = User.create_user('employee', 'employee')
        self.employee = self.login_as(employee)
        self._employee = employee

        manager = User.create_user('manager', 'manager')
        self.manager = self.login_as(manager)
        self._manager = manager

        self.client.json_post(reverse('siteapi:org_user', args=(self.org, )) + '?username=employee')

        group = Group.objects.create(name='test', parent=Group.valid_objects.filter(uid=org['manager_uid']).first())
        ManagerGroup.objects.create(group=group, scope_subject=2, apps=['app', 'demo'])
        GroupMember.objects.create(owner=group, user=manager)

    @mock.patch('siteapi.v1.serializers.app.SAMLAPPSerializer.gen_xml')
    @mock.patch('oneid_meta.models.app.SAMLAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oneid_meta.models.app.LDAPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oneid_meta.models.app.HTTPAPP.more_detail', new_callable=mock.PropertyMock)
    @mock.patch('oauth2_provider.models.Application.more_detail', new_callable=mock.PropertyMock)
    def test_create_app(
            self,
            mock_oauth_info,
            mock_http_info,
            mock_ldap_info,
            mock_saml_info,
            mock_gen_xml,
    ):
        mock_oauth_info.return_value = []
        mock_http_info.return_value = []
        mock_ldap_info.return_value = []
        mock_saml_info.return_value = []
        mock_gen_xml.side_effects = []
        res = self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)
        self.assertEqual(res.json(), APP_1_EXCEPT)

        res = self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_2)

        res = res.json()
        self.assertIn('client_id', res['oauth_app'])
        self.assertIn('client_secret', res['oauth_app'])
        del res['oauth_app']['client_id']
        del res['oauth_app']['client_secret']
        self.assertEqual(res, APP_2_EXCEPT)

        res = self.client.json_post(reverse('siteapi:app_list', args=(self.org, )),
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

        res = self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_3)
        self.assertEqual(res.status_code, 201)
        res = res.json()
        self.assertIn('acs', res['saml_app'])

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

        res = self.employee.json_post(reverse('siteapi:app_list', args=(self.org, )), data={'name': 'testname'})
        self.assertEqual(res.status_code, 403)

        perm, _ = Perm.objects.get_or_create(subject=self.org, scope='app', action='create')
        user_perm = UserPerm.get(self._employee, perm)
        user_perm.permit()

        res = self.employee.json_post(reverse('siteapi:app_list', args=(self.org, )), data={'name': 'testname'})

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

        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)
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
            'saml_app': None,
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

        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_2)
        app2 = APP.valid_objects.get(uid='test_uid')
        app2.editable = False
        app2.save()
        res = self.client.json_patch(reverse('siteapi:app_detail', args=('test_uid', )), data={'remark': 'new'})
        self.assertEqual(res.status_code, 405)

    def test_delete_app(self):
        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)
        self.assertTrue(APP.valid_objects.filter(uid=APP_1_EXCEPT['uid']).exists())
        self.assertTrue(Perm.valid_objects.filter(uid='app_demo_access').exists())

        res = self.client.delete(reverse('siteapi:app_detail', args=(APP_1_EXCEPT['uid'], )))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(APP.valid_objects.filter(uid=APP_1_EXCEPT['uid']).exists())
        self.assertTrue(APP.objects.filter(uid=APP_1_EXCEPT['uid'], is_del=True).exists())
        self.assertFalse(OAuthAPP.objects.filter(app__uid=APP_1_EXCEPT['uid']).exists())
        self.assertFalse(Perm.objects.filter(uid='app_demo_access').exists())

        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_2)
        app2 = APP.valid_objects.get(uid='test_uid')
        app2.editable = False
        app2.save()
        res = self.client.delete(reverse('siteapi:app_detail', args=('test_uid', )))
        self.assertEqual(res.status_code, 405)

    def test_app_list(self):
        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)
        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_2)
        res = self.client.get(reverse('siteapi:app_list', args=(self.org, )))
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

        res = self.client.get(reverse('siteapi:app_list', args=(self.org, )), data={'page_size': 1, 'page': 2})
        self.assertEqual(res.status_code, 200)

    def test_ucenter_app_list(self):
        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)

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

        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data={'uid': 'app', 'name': 'app'})
        res = self.employee.get(reverse('siteapi:app_list', args=(self.org, )))
        self.assertEqual(res.status_code, 403)
        res = self.manager.get(reverse('siteapi:app_list', args=(self.org, )))
        self.assertEqual(res.status_code, 200)

        res = self.employee.json_patch(reverse('siteapi:app_detail', args=('app', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 403)

        res = self.manager.json_patch(reverse('siteapi:app_detail', args=('app', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 200)

    def test_app_list_with(self):
        self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data=APP_1)

        res = self.employee.get(reverse('siteapi:app_list', args=(self.org, )),
                                data={
                                    'node_uid': 'd_root',
                                    'owner_access': True
                                })
        self.assertEqual(res.status_code, 403)

        res = self.manager.get(reverse('siteapi:app_list', args=(self.org, )),
                               data={
                                   'node_uid': 'd_root',
                                   'owner_access': True
                               })
        self.assertEqual(0, res.json()['count'])

        dept = Dept.objects.get(uid='root')
        perm = Perm.objects.get(uid='app_demo_access')
        owner_perm = dept.owner_perm_cls.get(dept, perm)
        owner_perm.permit()

        res = self.manager.get(reverse('siteapi:app_list', args=(self.org, )),
                               data={
                                   'node_uid': 'd_root',
                                   'owner_access': True
                               })
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
                'saml_app': None,
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

    def test_org_app(self):
        usr1 = User.create_user('usr1', 'usr1')
        self.usr1 = self.login_as(usr1)
        org1 = self.usr1.json_post(reverse('siteapi:org_create'), data={'name': 'org1'}).json()

        self.usr1.json_post(reverse('siteapi:app_list', args=(org1['oid'], )), data={'name': 'app1'}).json()
        self.usr1.json_post(reverse('siteapi:app_list', args=(org1['oid'], )), data={'name': 'app2'}).json()

        usr2 = User.create_user('usr2', 'usr2')
        self.usr2 = self.login_as(usr2)
        org2 = self.usr2.json_post(reverse('siteapi:org_create'), data={'name': 'org2'}).json()

        mgr = Group.valid_objects.create(uid='sub1',
                                         name='sub1',
                                         parent=Group.valid_objects.filter(uid=org1['manager_uid']).first())
        GroupMember.valid_objects.create(user=usr2, owner=mgr)
        ManagerGroup.objects.create(group=mgr, scope_subject=2, apps=['app2'])

        self.usr2.json_post(reverse('siteapi:app_list', args=(org2['oid'], )), data={'name': 'app3'}).json()
        self.usr2.json_post(reverse('siteapi:app_list', args=(org2['oid'], )), data={'name': 'app4'}).json()

        mgr = Group.valid_objects.create(uid='sub2',
                                         name='sub2',
                                         parent=Group.valid_objects.filter(uid=org2['manager_uid']).first())
        GroupMember.valid_objects.create(user=usr1, owner=mgr)
        ManagerGroup.objects.create(group=mgr, scope_subject=2, apps=['app4'])

        usr1_org1 = {
            app['name']
            for app in self.usr1.get(reverse('siteapi:app_list', args=(org1['oid'], ))).json()['results']
        }
        usr1_org2 = {
            app['name']
            for app in self.usr1.get(reverse('siteapi:app_list', args=(org2['oid'], ))).json()['results']
        }
        usr2_org1 = {
            app['name']
            for app in self.usr2.get(reverse('siteapi:app_list', args=(org1['oid'], ))).json()['results']
        }
        usr2_org2 = {
            app['name']
            for app in self.usr2.get(reverse('siteapi:app_list', args=(org2['oid'], ))).json()['results']
        }

        self.assertEqual(usr1_org1, {'app1', 'app2'})
        self.assertEqual(usr1_org2, {'app4'})
        self.assertEqual(usr2_org1, {'app2'})
        self.assertEqual(usr2_org2, {'app3', 'app4'})

        usr3 = User.create_user('usr3', 'usr3')
        self.usr3 = self.login_as(usr3)

        self.assertEqual(
            self.usr3.json_post(reverse('siteapi:app_list', args=(org1['oid'], )), data={
                'name': 'app5'
            }).status_code, 403)

        perm, _ = Perm.objects.get_or_create(subject=org1['oid'], scope='app', action='create')
        user_perm = UserPerm.get(usr3, perm)
        user_perm.permit()

        self.assertEqual(
            self.usr3.json_post(reverse('siteapi:app_list', args=(org2['oid'], )), data={
                'name': 'app5'
            }).status_code, 403)
        self.assertEqual(
            self.usr3.json_post(reverse('siteapi:app_list', args=(org1['oid'], )), data={
                'name': 'app5'
            }).json()['name'], 'app5')

    def test_create_app_empty_name(self):
        res = self.client.json_post(reverse('siteapi:app_list', args=(self.org, )), data={'name': '  '})
        self.assertEqual(res.json(), {"name": ["This field may not be blank."]})
