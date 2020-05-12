'''
tests for api about group
'''
# pylint: disable=missing-docstring,duplicate-code,too-many-lines, duplicate-code

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    Group,
    User,
    GroupMember,
    Perm,
    UserPerm,
    GroupPerm,
    ManagerGroup,
    APP,
)


class GroupTestCase(TestCase):
    mock_now = True

    def setUp(self):
        super(GroupTestCase, self).setUp()
        root = Group.valid_objects.get(uid='root')
        self.root = root
        role_group = Group.valid_objects.create(uid='role_group_1', name='role_group_1', parent=root, accept_user=False)
        role_1 = Group.valid_objects.create(uid='role_1', name='role_1', parent=role_group, order_no=2)
        Group.valid_objects.create(uid='role_2', name='role_2', parent=role_group, order_no=1)

        user = User.create_user('employee', 'employee')
        GroupMember.valid_objects.create(user=user, owner=role_1)
        user = User.create_user('employee_2', 'employee_2')
        self.employee = None

    def test_get_group_list(self):
        res = self.client.get(reverse('siteapi:group_list'))
        expect = {
            'count':
            3,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'group_id': 2,
                'uid': 'role_group_1',
                'node_uid': 'g_role_group_1',
                'node_subject': 'root',
                'name': 'role_group_1',
                'remark': '',
                'accept_user': False
            }, {
                'group_id': 3,
                'uid': 'role_1',
                'node_uid': 'g_role_1',
                'node_subject': 'root',
                'name': 'role_1',
                'remark': '',
                'accept_user': True
            }, {
                'group_id': 4,
                'uid': 'role_2',
                'node_uid': 'g_role_2',
                'node_subject': 'root',
                'name': 'role_2',
                'remark': '',
                'accept_user': True
            }]
        }
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:group_list'), data={'name': 'role_1'})
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'group_id': 3,
                'uid': 'role_1',
                'node_uid': 'g_role_1',
                'node_subject': 'root',
                'name': 'role_1',
                'remark': '',
                'accept_user': True
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_get_group_detail(self):
        res = self.client.get(reverse('siteapi:group_detail', args=('role_group_1', )))
        expect = {
            'parent_uid': 'root',
            'parent_node_uid': 'g_root',
            'parent_name': 'root',
            'group_id': 2,
            'uid': 'role_group_1',
            'node_uid': 'g_role_group_1',
            'node_subject': 'root',
            'name': 'role_group_1',
            'remark': '',
            'accept_user': False,
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(expect, res.json())

    def test_get_group_tree(self):
        res = self.client.get(reverse('siteapi:group_tree', args=('root', )))
        expect = {
            'info': {
                'group_id': 1,
                'uid': 'root',
                'node_uid': 'g_root',
                'node_subject': 'root',
                'name': 'root',
                'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
                'accept_user': False,
            },
            'groups': [{
                'info': {
                    'group_id': 2,
                    'uid': 'role_group_1',
                    'node_uid': 'g_role_group_1',
                    'node_subject': 'root',
                    'name': 'role_group_1',
                    'remark': '',
                    'accept_user': False,
                },
                'groups': [{
                    'info': {
                        'group_id': 4,
                        'uid': 'role_2',
                        'node_uid': 'g_role_2',
                        'node_subject': 'root',
                        'name': 'role_2',
                        'remark': '',
                        'accept_user': True,
                    },
                    'groups': []
                }, {
                    'info': {
                        'group_id': 3,
                        'uid': 'role_1',
                        'node_uid': 'g_role_1',
                        'node_subject': 'root',
                        'name': 'role_1',
                        'remark': '',
                        'accept_user': True,
                    },
                    'groups': []
                }]
            }]
        }
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:group_tree', args=('root', )), data={'user_required': True})
        expect = {
            'info': {
                'group_id': 1,
                'uid': 'root',
                'node_uid': 'g_root',
                'node_subject': 'root',
                'name': 'root',
                'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
                'accept_user': False,
            },
            'headcount':
            1,
            'groups': [{
                'info': {
                    'group_id': 2,
                    'uid': 'role_group_1',
                    'node_uid': 'g_role_group_1',
                    'node_subject': 'root',
                    'name': 'role_group_1',
                    'remark': '',
                    'accept_user': False,
                },
                'headcount':
                1,
                'groups': [{
                    'info': {
                        'group_id': 4,
                        'uid': 'role_2',
                        'node_uid': 'g_role_2',
                        'node_subject': 'root',
                        'name': 'role_2',
                        'remark': '',
                        'accept_user': True,
                    },
                    'headcount': 0,
                    'groups': [],
                    'users': []
                }, {
                    'info': {
                        'group_id': 3,
                        'uid': 'role_1',
                        'node_uid': 'g_role_1',
                        'node_subject': 'root',
                        'name': 'role_1',
                        'remark': '',
                        'accept_user': True,
                    },
                    'headcount': 1,
                    'groups': [],
                    'users': [{
                        'user_id': 2,
                        'username': 'employee',
                        'name': ''
                    }]
                }],
                'users': []
            }],
            'users': []
        }
        self.assertEqual(res.json(), expect)

    def test_delete_group(self):
        res = self.client.delete(reverse('siteapi:group_detail', args=('root', )))
        self.assertEqual(res.status_code, 400)
        self.assertTrue(Group.valid_objects.filter(uid='root').exists())

        user = User.objects.get(username='employee')
        group_member = GroupMember.objects.create(user=user, owner=Group.objects.get(uid='role_2'))
        res = self.client.delete(reverse('siteapi:group_detail', args=('role_2', )))
        self.assertEqual(res.status_code, 400)

        group_member.kill()
        res = self.client.delete(reverse('siteapi:group_detail', args=('role_2', )))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Group.valid_objects.filter(uid='role_2').exists())

    def test_delete_group_ignore_users(self):
        res = self.client.delete(reverse('siteapi:group_detail', args=('role_1', )))
        self.assertEqual(res.json(), {'node': ['protected_by_child_user']})
        self.assertEqual(res.status_code, 400)

        res = self.client.delete(reverse('siteapi:group_detail', args=('role_1', )) + "?ignore_user=True")
        self.assertEqual(res.status_code, 204)

    def test_update_group(self):
        res = self.client.json_patch(reverse('siteapi:group_detail', args=('root', )),
                                     data={
                                         'name': 'new_name',
                                         'ding_group': {
                                             'uid': 1,
                                             'data': '{"key": "val"}',
                                         },
                                         'visibility': 4,
                                         'node_scope': ['1'],
                                         'user_scope': ['2'],
                                     })
        expect = {
            'parent_uid': None,
            'parent_node_uid': None,
            'parent_name': None,
            'group_id': 1,
            'uid': 'root',
            'node_uid': 'g_root',
            'node_subject': 'root',
            'name': 'new_name',
            'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
            'accept_user': False,
            'ding_group': {
                'uid': 1,
                'data': '{"key": "val"}',
                'subject': 'role',
                'is_group': False,
            },
            'node_scope': ['1'],
            'user_scope': ['2'],
            'visibility': 4,
        }
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(reverse('siteapi:group_detail', args=('root', )), data={'visibility': 1})
        expect = {
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqualScoped(res.json(), expect, ['node_scope', 'user_scope', 'visibility'])

        res = self.client.json_patch(
            reverse('siteapi:group_detail', args=('root', )),
            data={'node_scope': {
                'as': 'sd'
            }},
        )
        self.assertEqual(400, res.status_code)

    def test_get_group_child_group(self):
        res = self.client.get(reverse('siteapi:group_child_group', args=('role_group_1', )))
        expect = {
            'groups': [{
                'group_id': 4,
                'uid': 'role_2',
                'node_uid': 'g_role_2',
                'node_subject': 'root',
                'name': 'role_2',
                'remark': '',
                'accept_user': True,
            }, {
                'group_id': 3,
                'uid': 'role_1',
                'node_uid': 'g_role_1',
                'node_subject': 'root',
                'name': 'role_1',
                'remark': '',
                'accept_user': True,
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_create_child_group(self):
        res = self.client.json_post(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                    data={
                                        'uid': 'role_3',
                                        'name': 'role_3',
                                        'ding_group': {
                                            'uid': 2,
                                        }
                                    })
        expect = {
            'group_id': 5,
            'uid': 'role_3',
            'node_uid': 'g_role_3',
            'node_subject': 'root',
            'name': 'role_3',
            'remark': '',
            'accept_user': True,
            'ding_group': {
                'uid': 2,
                'data': '{}',
                'subject': 'role',
                'is_group': False,
            },
            'parent_node_uid': 'g_role_group_1',
            'parent_uid': 'role_group_1',
            'parent_name': 'role_group_1',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(res.json(), expect)
        res = self.client.json_post(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                    data={
                                        'uid': 'role_3',
                                        'name': 'role_3',
                                        'ding_group': {
                                            'uid': 2,
                                        }
                                    })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'uid': ['this value has be used']})

    def test_ignore_manager_group(self):
        res = self.client.json_post(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                    data={
                                        "node_uid": "",
                                        "name": "后厨",
                                        "node_scope": [],
                                        "user_scope": [],
                                        "manager_group": {
                                            "nodes": [],
                                            "users": [],
                                            "perms": [],
                                            "apps": [],
                                            "scope_subject": 1
                                        },
                                        "users": []
                                    })
        self.assertEqual(res.json()['name'], '后厨')

    def test_create_category(self):
        employee, _ = User.objects.get_or_create(username='employee')
        Group.objects.create(uid='intra')
        self.employee = self.login_as(employee)

        res = self.employee.json_post(reverse('siteapi:group_child_group', args=('intra', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 403)

        perm, _ = Perm.objects.get_or_create(subject='system', scope='category', action='create')
        UserPerm.get(employee, perm).permit()

        res = self.employee.json_post(reverse('siteapi:group_child_group', args=('intra', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 201)

        self.assertEqual(len(list(employee.manager_groups)), 1)
        manager_group = list(employee.manager_groups)[0]
        self.assertEqual(manager_group.nodes, ['g_new'])
        self.assertEqual(manager_group.group.users, [employee])

    def test_auto_uid(self):
        res = self.client.json_post(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                    data={
                                        'name': '策划',
                                        'ding_group': {
                                            'uid': 2,
                                        }
                                    })
        self.assertEqual('cehua', res.json()['uid'])

    def test_update_child_group(self):
        res = self.client.json_patch(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                     data={
                                         'group_uids': ['role_1', 'role_2'],
                                         'subject': 'sort',
                                     })
        expect = {
            'groups': [
                {
                    'group_id': 3,
                    'uid': 'role_1',
                    'node_uid': 'g_role_1',
                    'node_subject': 'root',
                    'name': 'role_1',
                    'remark': '',
                    'accept_user': True,
                },
                {
                    'group_id': 4,
                    'uid': 'role_2',
                    'node_uid': 'g_role_2',
                    'node_subject': 'root',
                    'name': 'role_2',
                    'remark': '',
                    'accept_user': True,
                },
            ]
        }
        self.assertEqual(res.json(), expect)

        Group.valid_objects.create(uid='role_3', name='role_3')
        res = self.client.json_patch(reverse('siteapi:group_child_group', args=('role_group_1', )),
                                     data={
                                         'subject': 'add',
                                         'group_uids': ['role_3'],
                                     })
        expect = ['role_1', 'role_2', 'role_3']
        self.assertEqual(expect, [item['uid'] for item in res.json()['groups']])

    def test_get_group_child_user(self):
        res = self.client.get(reverse('siteapi:group_child_user', args=('role_1', )))
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'user_id':
                2,
                'hiredate':
                None,
                'last_active_time':
                None,
                'created':
                self.now_str,
                'remark':
                '',
                'avatar':
                '',
                'username':
                'employee',
                'is_settled':
                False,
                'has_password':
                True,
                'is_manager':
                False,
                'is_admin':
                False,
                'is_extern_user':
                False,
                'origin_verbose':
                '脚本添加',
                'name':
                '',
                'email':
                '',
                'position':
                '',
                'private_email':
                '',
                'mobile':
                '',
                'employee_number':
                '',
                'gender':
                0,
                'require_reset_password':
                False,
                'nodes': [{
                    'accept_user': True,
                    'group_id': 3,
                    'name': 'role_1',
                    'node_subject': 'root',
                    'node_uid': 'g_role_1',
                    'remark': '',
                    'uid': 'role_1'
                }],
            }]
        }
        self.assertEqual(res.json(), expect)

        user1 = User.valid_objects.get(username='employee')
        user2 = User.valid_objects.get(username='employee_2')
        role_2 = Group.valid_objects.get(uid='role_2')
        GroupMember.valid_objects.create(user=user1, owner=role_2)

        res = self.client.get(
            reverse('siteapi:group_child_user', args=('role_1', )),
            data={'uids': 'role_1|role_2'},
        )
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['username'], 'employee')

        GroupMember.valid_objects.create(user=user2, owner=role_2)
        res = self.client.get(reverse('siteapi:group_child_user', args=('role_1', )), data={'uids': 'role_1|role_2'})
        expect = ['employee', 'employee_2']
        self.assertEqual([user['username'] for user in res.json()['results']], expect)

    def test_update_group_child_user(self):
        url = reverse('siteapi:group_child_user', args=('role_1', ))
        res = self.client.json_patch(url, data={
            'subject': 'delete',
            'user_uids': ['employee'],
        })
        expect = {'users': []}
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(url, data={
            'subject': 'add',
            'user_uids': ['employee_2', 'employee'],
        })
        expect = ['employee_2', 'employee']
        self.assertEqual([user['username'] for user in res.json()['users']], expect)

        res = self.client.json_patch(url, data={
            'subject': 'sort',
            'user_uids': ['employee', 'employee_2'],
        })

        expect = ['employee', 'employee_2']
        self.assertEqual([user['username'] for user in res.json()['users']], expect)

        User.create_user('employee_3', 'employee_3')
        res = self.client.json_patch(url,
                                     data={
                                         'subject': 'override',
                                         'user_uids': ['employee_3', 'employee_2', 'employee'],
                                     })

        expect = ['employee_3', 'employee_2', 'employee']
        self.assertEqual([user['username'] for user in res.json()['users']], expect)

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

    def test_get_scope_list(self):
        res = self.client.get(reverse('siteapi:group_scope_list', args=('root', )))
        expect = [
            {
                'group_id': 1,
                'node_uid': 'g_root',
                'node_subject': 'root',
                'uid': 'root',
                'name': 'root',
                'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
                'accept_user': False,
                'parent_uid': None,
                'parent_node_uid': None
            },
            {
                'group_id': 2,
                'node_uid': 'g_role_group_1',
                'node_subject': 'root',
                'uid': 'role_group_1',
                'name': 'role_group_1',
                'remark': '',
                'accept_user': False,
                'parent_uid': 'root',
                'parent_node_uid': 'g_root'
            },
            {
                'group_id': 4,
                'node_uid': 'g_role_2',
                'node_subject': 'root',
                'uid': 'role_2',
                'name': 'role_2',
                'remark': '',
                'accept_user': True,
                'parent_uid': 'role_group_1',
                'parent_node_uid': 'g_role_group_1'
            },
            {
                'group_id': 3,
                'node_uid': 'g_role_1',
                'node_subject': 'root',
                'uid': 'role_1',
                'name': 'role_1',
                'remark': '',
                'accept_user': True,
                'parent_uid': 'role_group_1',
                'parent_node_uid': 'g_role_group_1'
            },
        ]
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:node_list', args=('g_root', )))
        self.assertEqual(expect, res.json())

    def test_group_user_search(self):
        role_group = Group.valid_objects.create(uid='group_3', name='group_3', parent=self.root, accept_user=False)
        role_3 = Group.valid_objects.create(uid='role_3', name='role_3', parent=role_group, order_no=3)
        user = User.create_user('zhangsan', 'zhangsan')
        user.name = '张三'
        user.email = '13412341233@qq.com'
        user.mobile = '13412341233'
        user.created = '2019-01-01T00:00:00+08:00'
        user.last_active_time = '2019-02-01T00:00:00+08:00'
        user.save()
        GroupMember.valid_objects.create(user=user, owner=role_3)
        user2 = User.create_user('zhangsi', 'zhangsi')
        user2.name = '张四'
        user2.email = '13412341234@qq.com'
        user2.mobile = '13412341234'
        user2.created = '2019-03-01T00:00:00+08:00'
        user2.last_active_time = '2019-04-01T00:00:00+08:00'
        user2.save()
        GroupMember.valid_objects.create(user=user2, owner=role_3)
        user3 = User.create_user('lisan', 'lisan')
        user3.name = '李三'
        user3.email = '13412341235@qq.com'
        user3.mobile = '13412341235'
        user3.created = '2019-05-01T00:00:00+08:00'
        user3.last_active_time = '2019-06-01T00:00:00+08:00'
        user3.save()
        GroupMember.valid_objects.create(user=user3, owner=role_3)
        user4 = User.create_user('lisi', 'lisi')
        user4.name = '李四'
        user4.email = '13412341236@qq.com'
        user4.mobile = '13412341236'
        user4.created = '2019-07-01T00:00:00+08:00'
        user4.last_active_time = '2019-08-01T00:00:00+08:00'
        user4.save()
        GroupMember.valid_objects.create(user=user4, owner=role_3)
        test_list = [{'email':'12341234'}, {'name':'张'}, {'username':'li'}, {'mobile':'12341234'}, \
            {'before_created':'2019-06-01T00:00:00+08:00'}, {'after_created':'2019-06-01T00:00:00+08:00'}, \
                {'before_last_active_time':'2019-03-01T00:00:00+08:00'}, \
                    {'after_last_active_time':'2019-03-01T00:00:00+08:00'}]
        result_list = []
        for test in test_list:
            res = self.client.get(reverse('siteapi:node_child_user', args=('g_role_3', )), data=test)
            result_list.append(res.json()['count'])
        expect = [1, 2, 2, 1, 3, 1, 1, 3]
        self.assertEqual(result_list, expect)
