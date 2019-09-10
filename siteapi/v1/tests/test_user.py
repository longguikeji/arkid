'''
tests for api about user
'''
# pylint: disable=missing-docstring

import json

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import DingUser, PosixUser, Group, Dept, User, CustomField, DeptMember

EMPLOYEE = {
    'user': {
        'user_id': 2,
        'avatar': '',
        'username': 'employee1',
        'name': 'employee1',
        'email': 'email',
        'mobile': '18812345678',
        'employee_number': '',
        'gender': 2,
        'private_email': '',
        'is_settled': False,
        'is_manager': False,
        'is_admin': False,
        'origin_verbose': '管理员添加',
        'position': '',
        'hiredate': None,
        'ding_user': {
            'uid': 'ding_employee2',
            'account': '18812345678',
            'data': '{"key": "val"}'
        },
    },
    'depts': [
        {
            'dept_id': 1,
            'name': 'root',
            'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
            'uid': 'root',
            'node_uid': 'd_root',
            'node_subject': 'dept'
        },
    ],
    'groups': [{
        'accept_user': False,
        'group_id': 1,
        'name': 'root',
        'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
        'uid': 'root',
        'node_uid': 'g_root',
        'node_subject': 'root',
    }],
    'nodes': [{
        'accept_user': False,
        'group_id': 1,
        'name': 'root',
        'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
        'uid': 'root',
        'node_uid': 'g_root',
        'node_subject': 'root',
    }, {
        'dept_id': 1,
        'name': 'root',
        'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
        'uid': 'root',
        'node_uid': 'd_root',
        'node_subject': 'dept'
    }]
}

USER_DATA = {
    'username': 'employee1',
    'name': 'employee1',
    'avatar': '',
    'email': 'email',
    'mobile': '18812345678',
    'private_email': '',
    'position': '',
    'gender': 2,
    'ding_user': {
        'uid': 'ding_employee2',
        'account': '18812345678',
        'data': '{"key": "val"}'
    },
}


class UserTestCase(TestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        DingUser.objects.create(user=self.user, account='18812341234', uid='admin')
        PosixUser.objects.create(user=self.user)
        Group.valid_objects.create(uid='test', name='test')
        Dept.valid_objects.create(uid='test', name='test')
        self.employee = None

    def create_user(self):
        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'group_uids': ['root'],
                                        'dept_uids': ['root'],
                                        'user': USER_DATA,
                                    })
        return res

    def test_username(self):
        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'group_uids': ['root'],
                                        'dept_uids': ['root'],
                                        'user': {
                                            'username': '测 ds'
                                        },
                                    })
        self.assertEqual(res.status_code, 400)
        self.assertEqual({'username': ['invalid']}, res.json())

        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'group_uids': ['root'],
                                        'dept_uids': ['root'],
                                        'user': {
                                            'username': ' ds'
                                        },
                                    })
        self.assertEqual(res.status_code, 201)

    def test_employee_create_user(self):
        employee = User.objects.create(username='employee')
        self.employee = self.login_as(employee)
        res = self.employee.json_post(reverse('siteapi:user_list'),
                                      data={
                                          'group_uids': ['root'],
                                          'dept_uids': ['root'],
                                          'user': USER_DATA,
                                      })
        self.assertEqual(res.status_code, 403)

        from oneid_meta.models import Perm, UserPerm
        perm, _ = Perm.objects.get_or_create(subject='system', scope='user', action='create')
        user_perm = UserPerm.get(employee, perm)
        user_perm.permit()
        res = self.employee.json_post(reverse('siteapi:user_list'),
                                      data={
                                          'group_uids': ['root'],
                                          'dept_uids': ['root'],
                                          'user': USER_DATA,
                                      })
        self.assertEqual(res.status_code, 201)

    def test_json_load_error(self):
        res = self.client.post(
            reverse('siteapi:user_list'),
            data=json.dumps({
                'group_uids': ['root'],
                'dept_uids': ['root'],
                'user': USER_DATA,
            })[:-1],
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 400)

    def test_get_user_list(self):
        User.objects.create(username='employee')
        res = self.client.get(reverse('siteapi:user_list'))
        expect = {
            'count':
            1,
            'next':
            None,
            'previous':
            None,
            'results': [{
                'user': {
                    'user_id': 2,
                    'username': 'employee',
                    'name': '',
                    'email': '',
                    'mobile': '',
                    'employee_number': '',
                    'gender': 0,
                    'avatar': '',
                    'private_email': '',
                    'position': '',
                    'is_settled': False,
                    'is_manager': False,
                    'is_admin': False,
                    'origin_verbose': '脚本添加',
                    'hiredate': None,
                },
                'groups': [],
                'depts': [],
                'nodes': []
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_create_user(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)

        self.assertEqual(res.json(), EMPLOYEE)

        User.valid_objects.get(username=USER_DATA['username']).delete()
        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'group_uids': ['root'],
                                        'dept_uids': ['none'],
                                        'user': USER_DATA,
                                    })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'dept_uids': ['dept:none does not exist']})

        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'user': {
                                            'username': 'employee2',
                                            'name': 'employee2',
                                            'email': 'email',
                                            'mobile': '18812345678',
                                            'gender': 2,
                                            'password': 'password',
                                            'avatar': '',
                                        },
                                    })
        self.assertEqual(User.valid_objects.get(username='employee2').password, '')

    def test_username_unique(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)
        res = self.create_user()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['existed']})

    def test_get_user(self):
        self.create_user()

        res = self.client.get(reverse('siteapi:user_detail', args=('employee1', )))
        self.assertEqual(res.json(), EMPLOYEE)

    def test_delete_user(self):
        self.create_user()

        res = self.client.delete(reverse('siteapi:user_detail', args=('employee1', )))
        self.assertEqual(res.status_code, 204)

        res = self.client.get(reverse('siteapi:user_detail', args=('employee1', )))

        self.assertEqual(res.status_code, 404)

    def test_update_user(self):
        self.create_user()
        cf = CustomField.valid_objects.create(name='忌口')    # pylint:disable=invalid-name
        patch_data = {
            'username': 'employee1',
            'name': 'new_employee1',
            'email': 'new_email',
            'mobile': '18812345678',
            'gender': 2,
            'is_settled': False,
            'private_email': 'private_email',
            'position': 'position',
            'ding_user': {
                'data': '{"key": "new_val"}',
            },
            'posix_user': {
                'uid': 500,
                'gid': 500,
            },
            'custom_user': {
                'data': {
                    cf.uuid.hex: '无',
                }
            },
            'hiredate': '2019-06-04T09:01:44+08:00',
        }

        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual(res.status_code, 200)
        expect = {
            'user_id': 2,
            'username': 'employee1',
            'avatar': '',
            'name': 'new_employee1',
            'email': 'new_email',
            'mobile': '18812345678',
            'employee_number': '',
            'private_email': 'private_email',
            'position': 'position',
            'is_settled': False,
            'is_manager': False,
            'is_admin': False,
            'origin_verbose': '管理员添加',
            'gender': 2,
            'ding_user': {
                'uid': 'ding_employee2',
                'account': '18812345678',
                'data': '{"key": "new_val"}'
            },
            'posix_user': {
                'uid': 500,
                'gid': 500,
                'pub_key': '',
                'home': ''
            },
            'custom_user': {
                'data': {
                    cf.uuid.hex: '无'
                },
                'pretty': [{
                    'uuid': cf.uuid.hex,
                    'name': '忌口',
                    'value': '无'
                }]
            },
            'hiredate': '2019-06-04T09:01:44+08:00',
        }
        self.assertEqual(expect, res.json()['user'])

    def test_get_user_group(self):
        self.create_user()
        res = self.client.get(reverse('siteapi:user_group', args=('employee1', )))
        expect = {
            'groups': [{
                'group_id': 1,
                'uid': 'root',
                'node_uid': 'g_root',
                'node_subject': 'root',
                'name': 'root',
                'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
                'accept_user': False
            }]
        }
        self.assertEqual(res.json(), expect)
        self.assertEqual(Group.valid_objects.count(), 2)

    def test_user_group_operations(self):
        self.create_user()
        res = self.client.json_patch(reverse('siteapi:user_group', args=('employee1', )), {
            'group_uids': ['test'],
            'subject': 'add'
        })
        expect = ['root', 'test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['groups']])

        res = self.client.json_patch(
            reverse('siteapi:user_group', args=('employee1', )),
            {
                'group_uids': ['root'],
                'subject': 'delete'
            },
        )
        expect = ['test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['groups']])

        res = self.client.json_patch(
            reverse('siteapi:user_group', args=('employee1', )),
            {
                'group_uids': ['root', 'test'],
                'subject': 'override'
            },
        )
        expect = ['root', 'test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['groups']])

    def test_get_user_dept(self):
        self.create_user()
        res = self.client.get(reverse('siteapi:user_dept', args=('employee1', )))
        expect = {
            'depts': [{
                'dept_id': 1,
                'uid': 'root',
                'node_uid': 'd_root',
                'node_subject': 'dept',
                'name': 'root',
                'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_user_dept_operations(self):
        self.create_user()
        res = self.client.json_patch(reverse('siteapi:user_dept', args=('employee1', )), {
            'dept_uids': ['test'],
            'subject': 'add'
        })
        expect = ['root', 'test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['depts']])

        res = self.client.json_patch(
            reverse('siteapi:user_dept', args=('employee1', )),
            {
                'dept_uids': ['root'],
                'subject': 'delete'
            },
        )
        expect = ['test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['depts']])

        res = self.client.json_patch(
            reverse('siteapi:user_dept', args=('employee1', )),
            {
                'dept_uids': ['root', 'test'],
                'subject': 'override'
            },
        )
        expect = ['root', 'test']
        self.assertEqual(expect, [item['uid'] for item in res.json()['depts']])


class UcenterUserTestCase(TestCase):
    def setUp(self):
        super(UcenterUserTestCase, self).setUp()

        Dept.objects.get(uid='root')
        self._employee = User.objects.create(username='employee')
        self.employee = self.login_as(self._employee)

        User.objects.create(username='test')

    def test_get_user_detail(self):
        res = self.employee.get(reverse('siteapi:ucenter_user_detail', args=('employee', )))
        self.assertEqual(200, res.status_code)

        res = self.employee.get(reverse('siteapi:ucenter_user_detail', args=('test', )))
        self.assertEqual(404, res.status_code)

        user = User.objects.get(username='test')
        DeptMember.objects.create(user=user, owner=Dept.objects.get(uid='root'))

        res = self.employee.get(reverse('siteapi:ucenter_user_detail', args=('test', )))
        self.assertEqual(200, res.status_code)
