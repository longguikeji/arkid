"""
tests for api about perm
"""

# pylint: disable=missing-docstring, too-many-lines
from django.urls import reverse
from siteapi.v1.tests import TestCase
from siteapi.v1.tests.test_node import create_node_tree
from oneid_meta.models import (
    Perm,
    User,
    UserPerm,
    Dept,
    DeptPerm,
    DeptMember,
    Group,
    GroupPerm,
    GroupMember,
)
from scripts.flush_perm import flush_all_perm

MAX_PERM_ID = 2

PERM_DATA = {
    'perm_id': MAX_PERM_ID + 1,
    'uid': 'app_app1_denglu',
    'name': '登录',
    'remark': '',
    'scope': 'app1',
    'action': 'denglu',
    'subject': 'app',
}

PERM_UID = 'app_app1_denglu'

PERM_WITH_OWNERS = {
    'perm_id': MAX_PERM_ID + 1,
    'uid': 'app_app1_denglu',
    'name': '登录',
    'remark': '',
    'scope': 'app1',
    'action': 'denglu',
    'subject': 'app',
    'permit_owners': {
        'count': 0,
        'has_more': False,
        'results': []
    },
    'reject_owners': {
        'count': 0,
        'has_more': False,
        'results': []
    },
}


class PermTestCase(TestCase):
    def setUp(self):
        super(PermTestCase, self).setUp()
        for perm in Perm.valid_objects.all():
            perm.kill()

    def create_perm(self, perm_data):
        res = self.client.json_post(reverse('siteapi:perm_list'), data=perm_data)
        return res

    def create_user(self):
        self.client.json_post(reverse('siteapi:user_list'),
                              data={
                                  'group_uids': ['root'],
                                  'dept_uids': ['root'],
                                  'user': {
                                      'username': 'employee1'
                                  },
                              })

    def test_perm(self):
        # # create
        res = self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})
        expect = PERM_DATA
        self.assertEqual(expect, res.json())

        # detail
        res = self.client.get(reverse('siteapi:perm_detail', args=('app_app1_denglu', )))
        self.assertEqual(expect, res.json())

        # list
        res = self.client.get(reverse('siteapi:perm_list'))
        expect = {'count': 1, 'next': None, 'previous': None, 'results': [PERM_WITH_OWNERS]}
        self.assertEqual(expect, res.json())

        # list query
        res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'app1'})
        expect = ['app_app1_denglu']
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])

        res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登'})
        expect = ['app_app1_denglu']
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])

        res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录1'})
        expect = []
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])

        res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'app2'})
        expect = []
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])
        res = self.client.get(reverse('siteapi:perm_list'), data={'action': 'access'})
        expect = []
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])
        res = self.client.get(reverse('siteapi:perm_list'), data={'action_except': 'access'})
        expect = ['app_app1_denglu']
        self.assertEqual(expect, [item['uid'] for item in res.json()['results']])

        # update
        res = self.client.json_patch(reverse('siteapi:perm_detail', args=('app_app1_denglu', )), data={'name': 'new'})
        expect = {
            'perm_id': MAX_PERM_ID + 1,
            'uid': 'app_app1_denglu',
            'name': 'new',
            'remark': '',
            'scope': 'app1',
            'action': 'denglu',
            'subject': 'app',
        }
        self.assertEqual(expect, res.json())

        # delete
        perm = Perm.valid_objects.get(uid='app_app1_denglu')
        perm.editable = False
        perm.save()
        res = self.client.delete(reverse('siteapi:perm_detail', args=('app_app1_denglu', )))
        self.assertEqual(res.status_code, 405)

        perm.editable = True
        perm.save()
        res = self.client.delete(reverse('siteapi:perm_detail', args=('app_app1_denglu', )))
        self.assertEqual(res.status_code, 204)

    def test_node_perm(self):
        res = self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})
        expect = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'status': 0,
                'perm': PERM_DATA,
                'value': False,
                'locked': False,
            }],
        }

        res = self.client.get(reverse('siteapi:dept_perm', args=('root', )))
        self.assertEqual(expect, res.json())
        res = self.client.get(reverse('siteapi:dept_perm', args=('root', )), data={'action': 'access'})
        self.assertEqual(0, res.json()['count'])
        res = self.client.get(reverse('siteapi:group_perm', args=('root', )))
        self.assertEqual(expect, res.json())
        res = self.client.get(reverse('siteapi:group_perm', args=('root', )), data={'action': 'access'})
        self.assertEqual(0, res.json()['count'])

        self.client.json_patch(reverse('siteapi:group_perm', args=('root', )),
                               data={
                                   'perm_statuses': [{
                                       'uid': 'app_app1_denglu',
                                       'status': 1
                                   }],
                               })
        res = self.client.get(reverse('siteapi:group_perm', args=('root', )))
        self.assertTrue(res.json()['results'][0]['value'])

        self.client.json_patch(reverse('siteapi:group_perm', args=('root', )),
                               data={
                                   'perm_statuses': [{
                                       'uid': 'app_app1_denglu',
                                       'status': -1
                                   }],
                               })
        res = self.client.get(reverse('siteapi:group_perm', args=('root', )))
        self.assertFalse(res.json()['results'][0]['value'])

    def test_user_perm(self):
        self.create_user()
        self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})

        # list
        res = self.client.get(reverse('siteapi:user_perm', args=('employee1', )))
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'status': 0,
                'dept_perm_value': False,
                'group_perm_value': False,
                'node_perm_value': False,
                'value': False,
                'perm': PERM_DATA,
            }]
        }
        self.assertEqual(res.json(), expect)

        # query
        res = self.client.get(reverse('siteapi:user_perm', args=('employee1', )), data={'action_except': 'access'})
        self.assertEqual(expect, res.json())

        # self
        user = User.objects.get(username='employee1')
        client = self.login_as(user)
        res = client.get(reverse('siteapi:user_self_perm'))
        expect = {'count': 0, 'next': None, 'previous': None, 'results': []}
        self.assertEqual(res.json(), expect)

        # update
        self.client.json_patch(reverse('siteapi:user_perm', args=('employee1', )),
                               data={
                                   'perm_statuses': [{
                                       'uid': 'app_app1_denglu',
                                       'status': 1
                                   }],
                               })

        res = client.get(reverse('siteapi:user_self_perm'))
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'perm': PERM_DATA,
                'status': 1,
                'dept_perm_value': False,
                'node_perm_value': False,
                'group_perm_value': False,
                'value': True,
            }]
        }
        self.assertEqual(res.json(), expect)


class PermOwnerTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})
        dept_perm = DeptPerm.objects.filter(perm__uid=PERM_UID).first()
        dept_perm.status = 1
        dept_perm.save()

        group_perm = GroupPerm.objects.filter(perm__uid=PERM_UID).first()
        group_perm.status = 1
        group_perm.save()

        user_perm = UserPerm.objects.filter(perm__uid=PERM_UID).first()
        user_perm.status = 1
        user_perm.value = True
        user_perm.save()

        self.perm = Perm.objects.get(uid=PERM_UID)

    def test_perm_list_with_owners(self):
        res = self.client.get(reverse('siteapi:perm_list'), data={'owner_subject': 'dept', 'scope': 'app1'})
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'perm_id': 3,
                'uid': 'app_app1_denglu',
                'name': '登录',
                'remark': '',
                'scope': 'app1',
                'action': 'denglu',
                'subject': 'app',
                'permit_owners': {
                    'count': 1,
                    'has_more': False,
                    'results': [{
                        'name': 'root',
                        'subject': 'dept',
                        'uid': 'd_root'
                    }]
                },
                'reject_owners': {
                    'count': 0,
                    'has_more': False,
                    'results': []
                },
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:perm_list'), data={'owner_subject': 'all', 'scope': 'app1'})
        expect = [{
            'uid': 'g_root',
            'name': 'root',
            'subject': 'root'
        }, {
            'uid': 'd_root',
            'name': 'root',
            'subject': 'dept'
        }, {
            'uid': 'admin',
            'name': '',
            'subject': 'user'
        }]
        self.assertEqual(expect, res.json()['results'][0]['permit_owners']['results'])
        res = self.client.get(reverse('siteapi:perm_list'), data={'scope': 'app1'})
        self.assertEqual(expect, res.json()['results'][0]['permit_owners']['results'])

    def test_perm_owners_page_in_perm_list(self):    # pylint: disable=invalid-name
        for index in range(21):
            dept = Dept.objects.create(uid=str(index), name=str(index))
            DeptPerm.objects.create(perm=self.perm, owner=dept, status=1)
        res = self.client.get(reverse('siteapi:perm_list'), data={'owner_subject': 'dept', 'scope': 'app1'})
        self.assertTrue(res.json()['results'][0]['permit_owners']['has_more'])

    def test_perm_owner(self):
        res = self.client.get(reverse('siteapi:perm_owner', args=(PERM_UID, )))
        expect = {
            'count':
            3,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'name': '',
                'uid': 'admin',
                'subject': 'user'
            }, {
                'name': 'root',
                'uid': 'd_root',
                'subject': 'dept'
            }, {
                'name': 'root',
                'uid': 'g_root',
                'subject': 'root',
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:perm_owner', args=(PERM_UID, )), data={'owner_subject': 'dept'})
        expect = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'name': 'root',
                'uid': 'd_root',
                'subject': 'dept'
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:perm_owner', args=(PERM_UID, )),
                              data={
                                  'owner_subject': 'user',
                                  'value': True
                              })
        expect = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{
                'name': '',
                'uid': 'admin',
                'subject': 'user'
            }]
        }
        self.assertEqual(expect, res.json())

    def test_patch_perm_owner(self):
        self.client.json_patch(reverse('siteapi:perm_owner', args=(PERM_UID, )),
                               data={
                                   'node_perm_status': [{
                                       'uid': 'd_root',
                                       'status': -1
                                   }],
                               })
        dept, _ = Dept.retrieve_node('d_root')
        owner_perm = dept.owner_perm_cls.get(dept, self.perm)
        self.assertFalse(owner_perm.value)

        self.client.json_patch(reverse('siteapi:perm_owner', args=(PERM_UID, )),
                               data={
                                   'user_perm_status': [{
                                       'uid': 'admin',
                                       'status': -1
                                   }],
                               })
        user = User.objects.get(username='admin')
        owner_perm = user.owner_perm_cls.get(user, self.perm)
        self.assertFalse(owner_perm.value)

        self.client.json_patch(reverse('siteapi:perm_owner', args=(PERM_UID, )),
                               data={
                                   'node_perm_status': [{
                                       'uid': 'd_root',
                                       'status': 1
                                   }],
                                   'user_perm_status': [{
                                       'uid': 'admin',
                                       'status': 1
                                   }],
                               })
        dept, _ = Dept.retrieve_node('d_root')
        owner_perm = dept.owner_perm_cls.get(dept, self.perm)
        self.assertTrue(owner_perm.value)

        user = User.objects.get(username='admin')
        owner_perm = user.owner_perm_cls.get(user, self.perm)
        self.assertTrue(owner_perm.value)


class PermSourceTestCase(TestCase):
    def setUp(self):
        super().setUp()

        tree = {
            '1': {
                '1-1': {
                    '1-1-1': {
                        '1-1-1-1': {},
                    },
                    '1-1-2': {},
                },
                '1-2': {
                    '1-2-1': {},
                    '1-2-2': {},
                },
                '1-3': {
                    '1-3-1': {},
                    '1-3-2': {},
                    '1-3-3': {},
                }
            }
        }

        list(create_node_tree(Dept, tree))
        list(create_node_tree(Group, tree))

    def test_perm_source(self):
        user = User.objects.create(username='test')
        self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})
        perm_uid = 'app_app1_denglu'
        for uid in [
                '1-1',
                '1-1-1',
                '1-1-1-1',
                '1-2-1',
                '1-3',
        ]:
            dept = Dept.objects.get(uid=uid)
            DeptMember.objects.create(user=user, owner=dept)
        for uid in [
                '1-1',
                '1-1-1-1',
                '1-3',
        ]:
            dept_perm = DeptPerm.objects.get(perm__uid=perm_uid, owner__uid=uid)
            dept_perm.permit()

        for uid in [
                '1',
                '1-1-2',
                '1-2',
                '1-2-2',
                '1-3-1',
        ]:
            group = Group.objects.get(uid=uid)
            GroupMember.objects.create(user=user, owner=group)
        for uid in [
                '1',
                '1-2',
                '1-3-1',
        ]:
            group_perm = GroupPerm.objects.get(perm__uid=perm_uid, owner__uid=uid)
            group_perm.permit()

        flush_all_perm()
        res = self.client.get(reverse('siteapi:user_perm_detail', args=('test', perm_uid)))
        expect = {
            'perm': {
                'perm_id': 3,
                'uid': 'app_app1_denglu',
                'name': '登录',
                'remark': '',
                'scope': 'app1',
                'action': 'denglu',
                'subject': 'app',
            },
            'status':
            0,
            'dept_perm_value':
            True,
            'group_perm_value':
            True,
            'node_perm_value':
            True,
            'value':
            True,
            'source': [{
                'name': '1-1',
                'uid': '1-1',
                'node_uid': 'd_1-1',
                'node_subject': 'dept',
            }, {
                'name': '1-1-1-1',
                'uid': '1-1-1-1',
                'node_uid': 'd_1-1-1-1',
                'node_subject': 'dept',
            }, {
                'name': '1-3',
                'uid': '1-3',
                'node_uid': 'd_1-3',
                'node_subject': 'dept',
            }, {
                'name': '1',
                'uid': '1',
                'node_uid': 'g_1',
                'node_subject': 'root',
            }, {
                'name': '1-2',
                'uid': '1-2',
                'node_uid': 'g_1-2',
                'node_subject': 'root',
            }, {
                'name': '1-3-1',
                'uid': '1-3-1',
                'node_uid': 'g_1-3-1',
                'node_subject': 'root',
            }]
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:user_perm_result', args=('test', perm_uid)))
        expect = {
            'perm': {
                'perm_id': 3,
                'uid': 'app_app1_denglu',
                'name': '登录',
                'remark': '',
                'scope': 'app1',
                'action': 'denglu',
                'subject': 'app',
            },
            'status': 0,
            'dept_perm_value': True,
            'group_perm_value': True,
            'node_perm_value': True,
            'value': True,
        }
        self.assertEqual(res.json(), expect)

    def test_perm_realtime(self):
        user = User.objects.create(username='test')
        self.client.json_post(reverse('siteapi:perm_list'), data={'scope': 'app1', 'name': '登录'})
        perm_uid = 'app_app1_denglu'

        # 对 user 所在的 dept 授予权限
        dept = Dept.objects.get(uid='1')
        DeptMember.objects.create(user=user, owner=dept)
        self.client.json_patch(reverse('siteapi:perm_owner', args=(perm_uid, )),
                               data={'node_perm_status': [{
                                   'uid': 'd_1',
                                   'status': 1,
                               }]})

        # 未实时生效
        url = reverse('siteapi:user_perm_detail', args=('test', perm_uid))
        res = self.client.get(url)
        expect = {
            'dept_perm_value': False,
            'group_perm_value': False,
            'status': 0,
            'value': False,
            'source': [],
        }
        self.assertEqualScoped(res.json(), expect, expect.keys())

        # 手动触发更新，获取实时判定结果
        res = self.client.json_put(url)
        expect = {
            'dept_perm_value': True,
            'group_perm_value': False,
            'status': 0,
            'value': True,
            'source': [{
                'name': '1',
                'uid': '1',
                'node_uid': 'd_1',
                'node_subject': 'dept'
            }],
        }
        self.assertEqualScoped(res.json(), expect, expect.keys())
