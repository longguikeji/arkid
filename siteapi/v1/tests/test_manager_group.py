'''
tests for api about manager group
'''
# pylint: disable=missing-docstring,duplicate-code,too-many-lines, duplicate-code

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    Group,
    User,
    GroupMember,
    Perm,
    GroupPerm,
    ManagerGroup,
    APP,
)


class ManagerGroupTestCase(TestCase):
    mock_now = True

    def setUp(self):
        super(ManagerGroupTestCase, self).setUp()
        root = Group.valid_objects.get(uid='root')
        self.root = root
        role_group = Group.valid_objects.create(uid='role_group_1', name='role_group_1', parent=root, accept_user=False)
        role_1 = Group.valid_objects.create(uid='role_1', name='role_1', parent=role_group, order_no=2)
        Group.valid_objects.create(uid='role_2', name='role_2', parent=role_group, order_no=1)

        user = User.create_user('employee', 'employee')
        GroupMember.valid_objects.create(user=user, owner=role_1)
        user = User.create_user('employee_2', 'employee_2')
        self.employee = None

    def test_manager_group(self):
        Group.objects.create(uid='manager', parent=self.root)
        Group.objects.create(uid='n1', parent=self.root)
        Group.objects.create(uid='n2', parent=self.root)
        perm1 = Perm.objects.create(subject='system', scope='demo', action='access')
        perm2 = Perm.objects.create(subject='system', scope='demo', action='admin')
        res = self.client.json_post(reverse('siteapi:group_child_group', args=('manager', )),
                                    data={
                                        'manager_group': {
                                            'nodes': ['g_n1'],
                                            'users': ['u1'],
                                            'apps': ['app1'],
                                            'perms': ['system_demo_access'],
                                            'scope_subject': 2,
                                        }
                                    })
        uid = res.json()['uid']
        self.assertTrue(GroupPerm.valid_objects.get(perm=perm1, owner__uid=uid).value)
        self.assertFalse(GroupPerm.valid_objects.get(perm=perm2, owner__uid=uid).value)

        expect = {
            'nodes': ['g_n1'],
            'users': ['u1'],
            'apps': ['app1'],
            'perms': ['system_demo_access'],
            'scope_subject': 2
        }
        self.assertEqual(expect, res.json()['manager_group'])

        res = self.client.json_patch(reverse('siteapi:group_detail', args=(uid, )),
                                     data={'manager_group': {
                                         'nodes': ['g_n2'],
                                         'perms': ['system_demo_admin'],
                                     }})
        expect = {
            'nodes': ['g_n2'],
            'users': ['u1'],
            'apps': ['app1'],
            'perms': ['system_demo_admin'],
            'scope_subject': 2,
        }
        self.assertEqual(expect, res.json()['manager_group'])
        self.assertEqual(GroupPerm.valid_objects.get(perm=perm1, owner__uid=uid).status, 0)
        self.assertTrue(GroupPerm.valid_objects.get(perm=perm2, owner__uid=uid).value)

        manager_group = ManagerGroup.objects.get(group__uid=uid)
        self.assertEqual(manager_group.nodes, ['g_n2'])
        node_2 = Group.objects.get(uid='n2')
        node_2.delete()
        res = self.client.get(reverse('siteapi:group_child_group', args=('manager', )))
        manager_group.refresh_from_db()
        self.assertEqual(manager_group.nodes, [])

    def test_manager_group_list(self):
        APP.objects.create(uid='demo', name='test')
        Perm.objects.create(subject='app', scope='demo', action='access')
        parent = Group.objects.create(uid='manager')

        group = Group.objects.create(uid='manager_group_1', parent=parent)
        GroupMember.objects.create(owner=group, user=User.objects.get(username='employee'))
        ManagerGroup.objects.create(group=group,
                                    scope_subject=2,
                                    users=['employee'],
                                    perms=['app_demo_access'],
                                    nodes=['root'],
                                    apps=['demo'])
        res = self.client.get(reverse('siteapi:node_child_node', args=('g_manager', )))
        expect = {
            'nodes': [{
                'parent_uid': 'manager',
                'parent_node_uid': 'g_manager',
                'parent_name': '',
                'group_id': 6,
                'node_uid': 'g_manager_group_1',
                'node_subject': 'root',
                'uid': 'manager_group_1',
                'name': '',
                'remark': '',
                'accept_user': True,
                'manager_group': {
                    'nodes': [],
                    'users': [{
                        'name': '',
                        'username': 'employee'
                    }],
                    'apps': [{
                        'uid': 'demo',
                        'name': 'test'
                    }],
                    'perms': [{
                        'uid': 'app_demo_access',
                        'name': ''
                    }],
                    'scope_subject': 2
                },
                'visibility': 1,
                'node_scope': [],
                'user_scope': [],
                'users': [{
                    'user_id': 2,
                    'username': 'employee',
                    'name': ''
                }]
            }]
        }
        self.assertEqual(expect, res.json())

    def test_app_perm(self):
        APP.objects.create(uid='app1', name='app1')
        APP.objects.create(uid='app2', name='app2')
        Group.objects.create(uid='manager', parent=self.root)
        res = self.client.json_post(
            reverse('siteapi:group_child_group', args=('manager', )),
            data={'manager_group': {
                'nodes': ['g_n1'],
                'users': ['u1'],
                'apps': ['app1'],
                'scope_subject': 2,
            }})

        manager_group = Group.valid_objects.get(uid=res.json()['uid'])
        user = User.valid_objects.get(username='employee')
        GroupMember.valid_objects.get_or_create(owner=manager_group, user=user)

        client = self.login_as(user)
        # 子管理为管理范围内的应用创建权限
        res = client.json_post(reverse('siteapi:perm_list'), data={
            'name': 'p1',
            'scope': 'app1',
        })
        self.assertEqual(res.status_code, 201)

        # 应用不在子管理员权限范围内
        res = client.json_post(reverse('siteapi:perm_list'), data={
            'name': 'p1',
            'scope': 'app2',
        })
        self.assertEqual(res.status_code, 403)

        # 超管可以任意创建
        res = self.client.json_post(reverse('siteapi:perm_list'), data={
            'name': 'p1',
            'scope': 'app2',
        })
        self.assertEqual(res.status_code, 201)
