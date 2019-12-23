'''
tests for api about dept
'''
# pylint: disable=missing-docstring,duplicate-code,too-many-lines

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import Dept, User, DeptMember


class DeptTestCase(TestCase):
    mock_now = True

    def setUp(self):
        super(DeptTestCase, self).setUp()
        root = Dept.valid_objects.get(uid='root')
        level_1 = Dept.valid_objects.create(uid='level_1', name='level_1', parent=root)
        Dept.valid_objects.create(uid='level_2-1', name='level_2-1', parent=level_1, order_no=2)
        Dept.valid_objects.create(uid='level_2-2', name='level_2-2', parent=level_1, order_no=1)
        user = User.create_user('employee', 'employee')
        DeptMember.valid_objects.create(user=user, owner=root)
        user = User.create_user('employee_2', 'employee_2')

    def test_get_dept_detail(self):
        res = self.client.get(reverse('siteapi:dept_detail', args=('level_1', )))
        expect = {
            'parent_uid': 'root',
            'parent_node_uid': 'd_root',
            'parent_name': 'root',
            'dept_id': 2,
            'uid': 'level_1',
            'node_uid': 'd_level_1',
            'node_subject': 'dept',
            'name': 'level_1',
            'remark': '',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:node_detail', args=('level_1', )))

    def test_get_dept_list(self):
        res = self.client.get(reverse('siteapi:dept_list'))
        expect = {
            'count':
            3,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'dept_id': 2,
                'uid': 'level_1',
                'node_uid': 'd_level_1',
                'node_subject': 'dept',
                'name': 'level_1',
                'remark': '',
            }, {
                'dept_id': 3,
                'uid': 'level_2-1',
                'node_uid': 'd_level_2-1',
                'node_subject': 'dept',
                'name': 'level_2-1',
                'remark': '',
            }, {
                'dept_id': 4,
                'uid': 'level_2-2',
                'node_uid': 'd_level_2-2',
                'node_subject': 'dept',
                'name': 'level_2-2',
                'remark': '',
            }]
        }
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:dept_list'), data={'name': '2-1'})
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'dept_id': 3,
                'uid': 'level_2-1',
                'name': 'level_2-1',
                'node_uid': 'd_level_2-1',
                'node_subject': 'dept',
                'remark': '',
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_get_dept_tree(self):
        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )), data={'user_required': True})
        expect = {
            'info': {
                'dept_id': 1,
                'uid': 'root',
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'name': 'root',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
            },
            'headcount':
            1,
            'users': [{
                'user_id': 2,
                'username': 'employee',
                'name': ''
            }],
            'depts': [{
                'info': {
                    'dept_id': 2,
                    'uid': 'level_1',
                    'node_uid': 'd_level_1',
                    'node_subject': 'dept',
                    'name': 'level_1',
                    'remark': '',
                },
                'headcount':
                0,
                'users': [],
                'depts': [
                    {
                        'info': {
                            'dept_id': 4,
                            'uid': 'level_2-2',
                            'node_uid': 'd_level_2-2',
                            'node_subject': 'dept',
                            'name': 'level_2-2',
                            'remark': '',
                        },
                        'headcount': 0,
                        'users': [],
                        'depts': []
                    },
                    {
                        'info': {
                            'dept_id': 3,
                            'uid': 'level_2-1',
                            'node_uid': 'd_level_2-1',
                            'node_subject': 'dept',
                            'name': 'level_2-1',
                            'remark': '',
                        },
                        'headcount': 0,
                        'users': [],
                        'depts': []
                    },
                ]
            }]
        }
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:dept_tree', args=('root', )), data={'user_required': False})
        expect = {
            'info': {
                'dept_id': 1,
                'uid': 'root',
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'name': 'root',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
            },
            'depts': [{
                'info': {
                    'dept_id': 2,
                    'uid': 'level_1',
                    'node_uid': 'd_level_1',
                    'node_subject': 'dept',
                    'name': 'level_1',
                    'remark': '',
                },
                'depts': [
                    {
                        'info': {
                            'dept_id': 4,
                            'uid': 'level_2-2',
                            'node_uid': 'd_level_2-2',
                            'node_subject': 'dept',
                            'name': 'level_2-2',
                            'remark': '',
                        },
                        'depts': []
                    },
                    {
                        'info': {
                            'dept_id': 3,
                            'uid': 'level_2-1',
                            'node_uid': 'd_level_2-1',
                            'node_subject': 'dept',
                            'name': 'level_2-1',
                            'remark': '',
                        },
                        'depts': []
                    },
                ]
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_delete_dept(self):
        res = self.client.delete(reverse('siteapi:dept_detail', args=('root', )))
        self.assertEqual(res.status_code, 400)
        self.assertTrue(Dept.valid_objects.filter(uid='root').exists())

        dept_member = DeptMember.objects.create(user=User.objects.get(username='employee'),
                                                owner=Dept.objects.get(uid='level_2-1'))
        res = self.client.delete(reverse('siteapi:dept_detail', args=('level_2-1', )))
        self.assertEqual(res.status_code, 400)

        dept_member.kill()
        res = self.client.delete(reverse('siteapi:dept_detail', args=('level_2-1', )))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Dept.valid_objects.filter(uid='level_2-1').exists())

    def test_update_dept(self):
        res = self.client.json_patch(reverse('siteapi:dept_detail', args=('level_1', )),
                                     data={
                                         'name': 'new_name',
                                         'remark': 'new_remark',
                                         'ding_dept': {
                                             'uid': 1,
                                             'data': '{"key": "val"}',
                                         },
                                         'visibility': 4,
                                         'node_scope': ['1'],
                                         'user_scope': ['2'],
                                     })
        expect = {
            'parent_uid': 'root',
            'parent_node_uid': 'd_root',
            'parent_name': 'root',
            'dept_id': 2,
            'uid': 'level_1',
            'node_uid': 'd_level_1',
            'node_subject': 'dept',
            'name': 'new_name',
            'remark': 'new_remark',
            'ding_dept': {
                'uid': 1,
                'data': '{"key": "val"}'
            },
            'node_scope': ['1'],
            'user_scope': ['2'],
            'visibility': 4,
        }
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(
            reverse('siteapi:dept_detail', args=('level_1', )),
            data={'node_scope': {
                'as': 'sd'
            }},
        )
        self.assertEqual(400, res.status_code)

    def test_get_dept_child_dept(self):
        res = self.client.get(reverse('siteapi:dept_child_dept', args=('level_1', )))
        expect = {
            'depts': [
                {
                    'dept_id': 4,
                    'uid': 'level_2-2',
                    'node_uid': 'd_level_2-2',
                    'node_subject': 'dept',
                    'name': 'level_2-2',
                    'remark': '',
                },
                {
                    'dept_id': 3,
                    'uid': 'level_2-1',
                    'node_uid': 'd_level_2-1',
                    'node_subject': 'dept',
                    'name': 'level_2-1',
                    'remark': '',
                },
            ]
        }
        self.assertEqual(res.json(), expect)

    def test_create_child_dept(self):
        res = self.client.json_post(reverse('siteapi:dept_child_dept', args=('level_1', )),
                                    data={
                                        'uid': 'level_2-3',
                                        'name': 'level_2-3',
                                        'ding_dept': {
                                            'uid': 1,
                                            'data': '{"key": "val"}',
                                        }
                                    })
        expect = {
            'dept_id': 5,
            'uid': 'level_2-3',
            'node_uid': 'd_level_2-3',
            'node_subject': 'dept',
            'name': 'level_2-3',
            'remark': '',
            'ding_dept': {
                'uid': 1,
                'data': '{"key": "val"}'
            },
            'parent_node_uid': 'd_level_1',
            'parent_uid': 'level_1',
            'parent_name': 'level_1',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1,
        }
        self.assertEqual(res.json(), expect)

        res = self.client.json_post(reverse('siteapi:dept_child_dept', args=('level_1', )),
                                    data={
                                        'uid': 'level_2-3',
                                        'name': 'level_2-3',
                                        'ding_dept': {
                                            'uid': 1,
                                            'data': '{"key": "val"}',
                                        }
                                    })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'uid': ['this value has be used']})

    def test_auto_uid(self):
        res = self.client.json_post(reverse('siteapi:dept_child_dept', args=('level_1', )), data={
            'name': '策划',
        })
        self.assertEqual(res.json()['uid'], 'cehua')

    def test_update_child_dept(self):
        res = self.client.json_patch(reverse('siteapi:dept_child_dept', args=('level_1', )),
                                     data={
                                         'dept_uids': ['level_2-1', 'level_2-2'],
                                         'subject': 'sort',
                                     })
        expect = {
            'depts': [
                {
                    'dept_id': 3,
                    'uid': 'level_2-1',
                    'node_uid': 'd_level_2-1',
                    'node_subject': 'dept',
                    'name': 'level_2-1',
                    'remark': '',
                },
                {
                    'dept_id': 4,
                    'uid': 'level_2-2',
                    'node_uid': 'd_level_2-2',
                    'node_subject': 'dept',
                    'name': 'level_2-2',
                    'remark': '',
                },
            ]
        }
        self.assertEqual(res.json(), expect)
        expect = ['level_2-1', '']

        Dept.valid_objects.create(uid='level_2-3', name='level_2-3')
        res = self.client.json_patch(reverse('siteapi:dept_child_dept', args=('level_1', )),
                                     data={
                                         'dept_uids': ['level_2-3'],
                                         'subject': 'add',
                                     })
        expect = ['level_2-1', 'level_2-2', 'level_2-3']
        self.assertEqual([item['uid'] for item in res.json()['depts']], expect)

    def test_get_dept_child_user(self):
        res = self.client.get(reverse('siteapi:dept_child_user', args=('root', )))
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
                'created':
                self.now_str,
                'last_active_time':
                None,
                'hiredate':
                None,
                'remark':
                '',
                'username':
                'employee',
                'name':
                '',
                'email':
                '',
                'is_settled':
                False,
                'is_manager':
                False,
                'is_admin':
                False,
                'is_extern_user':
                False,
                'origin_verbose':
                '脚本添加',
                'mobile':
                '',
                'position':
                '',
                'private_email':
                '',
                'employee_number':
                '',
                'gender':
                0,
                'avatar':
                '',
                'has_password':
                True,
                'require_reset_password':
                False,
                'nodes': [{
                    'dept_id': 1,
                    'name': 'root',
                    'node_subject': 'dept',
                    'node_uid': 'd_root',
                    'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
                    'uid': 'root'
                }],
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_update_dept_child_user(self):
        url = reverse('siteapi:dept_child_user', args=('root', ))
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

        # test batch move out
        Dept.objects.create(uid='another', name='another')
        self.client.json_patch(url,
                               data={
                                   'subject': 'move_out',
                                   'user_uids': ['employee_3', 'employee_2'],
                                   'dept_uids': ['another']
                               })

        res = self.client.get(url)
        expect = set(['employee'])
        self.assertEqual(
            set([user['username'] for user in res.json()['results']]),    # pylint:disable=consider-using-set-comprehension
            expect,
        )

        res = self.client.get(reverse('siteapi:dept_child_user', args=('another', )))
        expect = set(['employee_3', 'employee_2'])
        self.assertEqual(expect, set([user['username'] for user in res.json()['results']]))    # pylint:disable=consider-using-set-comprehension

        # test batch move inpalce
        res = self.client.json_patch(reverse('siteapi:dept_child_user', args=('another', )),
                                     data={
                                         'subject': 'move_out',
                                         'user_uids': ['employee_3', 'employee_2'],
                                         'dept_uids': ['another'],
                                     })
        res = self.client.get(reverse('siteapi:dept_child_user', args=('another', )))
        expect = set(['employee_3', 'employee_2'])
        self.assertEqual(expect, set([user['username'] for user in res.json()['results']]))    # pylint:disable=consider-using-set-comprehension

    def test_scope_list(self):
        res = self.client.get(reverse('siteapi:dept_scope_list', args=('root', )))
        expect = [
            {
                'dept_id': 1,
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'uid': 'root',
                'name': 'root',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
                'parent_uid': None,
                'parent_node_uid': None
            },
            {
                'dept_id': 2,
                'node_uid': 'd_level_1',
                'node_subject': 'dept',
                'uid': 'level_1',
                'name': 'level_1',
                'remark': '',
                'parent_uid': 'root',
                'parent_node_uid': 'd_root'
            },
            {
                'dept_id': 4,
                'node_uid': 'd_level_2-2',
                'node_subject': 'dept',
                'uid': 'level_2-2',
                'name': 'level_2-2',
                'remark': '',
                'parent_uid': 'level_1',
                'parent_node_uid': 'd_level_1'
            },
            {
                'dept_id': 3,
                'node_uid': 'd_level_2-1',
                'node_subject': 'dept',
                'uid': 'level_2-1',
                'name': 'level_2-1',
                'remark': '',
                'parent_uid': 'level_1',
                'parent_node_uid': 'd_level_1'
            },
        ]
        self.assertEqual(expect, res.json())

        res = self.client.get(reverse('siteapi:node_list', args=('d_root', )))
        self.assertEqual(expect, res.json())

    def test_create_dept_special_name(self):
        '''测试创建全特殊字符部门
        '''
        client = self.client
        data = {
            'node_uid': '',
            'name': "@@@",
            'node_scope': [],
            'user_scope': [],
            'manager_group': {
                'nodes': [],
                'users': [],
                'perms': [],
                'apps': [],
                'scope_subject': 1
            },
            'users': []
        }
        res = client.json_post(reverse('siteapi:node_child_node', args=('d_root', )), data=data)
        self.assertEqual(res.status_code, 201)
