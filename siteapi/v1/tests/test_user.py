'''
tests for api about user
'''
# pylint: disable=missing-docstring, too-many-lines

import json

from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    DingUser,
    PosixUser,
    Group,
    Dept,
    User,
    CustomField,
    DeptMember,
    Perm,
    UserPerm,
    WechatUser,
    Org,
)

EMPLOYEE = {
    'user': {
        'avatar': '',
        'username': 'employee1',
        'name': 'employee1',
        'mobile': '18812345678',
        'gender': 2,
        'private_email': '',
        'is_settled': False,
        'is_manager': False,
        'is_admin': False,
        'is_extern_user': False,
        'origin_verbose': '管理员添加',
        'last_active_time': None,
        'created': TestCase.now_str,
        'require_reset_password': False,
        'has_password': False,
        'ding_user': {
            'uid': 'ding_employee2',
            'account': '18812345678',
            'data': '{"key": "val"}'
        },
    },
    'depts': [
        {
            'name': 'root',
            'remark': '所有顶级的部门的父级，可视为整个公司。请勿修改',
            'uid': 'root',
            'node_uid': 'd_root',
            'node_subject': 'dept'
        },
    ],
    'groups': [{
        'accept_user': False,
        'name': 'root',
        'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
        'uid': 'root',
        'node_uid': 'g_root',
        'node_subject': 'root',
    }],
    'nodes': [{
        'accept_user': False,
        'name': 'root',
        'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
        'uid': 'root',
        'node_uid': 'g_root',
        'node_subject': 'root',
    }, {
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
    'mobile': '18812345678',
    'private_email': '',
    'gender': 2,
    'ding_user': {
        'uid': 'ding_employee2',
        'account': '18812345678',
        'data': '{"key": "val"}'
    },
}


class UserTestCase(TestCase):

    mock_now = True

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

    def test_query_userlist(self):
        '''模糊搜索用户列表
        '''
        self.create_user()
        client = self.client
        res = client.get(reverse('siteapi:user_list'), data={'keyword': '188'})
        user_list = res.json()['results']
        expect_count = 1
        self.assertEqual(expect_count, len(user_list))

        res = client.get(reverse('siteapi:user_list'), data={'keyword': '189'})
        user_list = res.json()['results']
        expect_count = 0
        self.assertEqual(expect_count, len(user_list))

        WechatUser.objects.create(
            user=User.valid_objects.get(username='employee1'),
            unionid='unionid-1',
        )
        res = client.get(reverse('siteapi:user_list'), data={'keyword': '188', 'wechat_unionid': 'unionid-1'})
        self.assertEqual(1, res.json()['count'])
        res = client.get(reverse('siteapi:user_list'), data={'keyword': '188', 'wechat_unionid': 'unionid-2'})
        self.assertEqual(0, res.json()['count'])

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
                                            'username': 'fdsfds'
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
                    'created': self.now_str,
                    'username': 'employee',
                    'name': '',
                    'mobile': '',
                    'last_active_time': None,
                    'gender': 0,
                    'avatar': '',
                    'private_email': '',
                    'nodes': [],
                    'is_settled': False,
                    'is_manager': False,
                    'is_admin': False,
                    'is_extern_user': False,
                    'origin_verbose': '脚本添加',
                    'require_reset_password': False,
                    'has_password': False,
                },
                'groups': [],
                'depts': [],
                'nodes': []
            }]
        }
        self.assertEqual(res.json(), expect)

    def test_org_user_detail(self):
        org1 = Org.create(name='org1', owner=User.valid_objects.get(username='admin'))
        org2 = Org.create(name='org2', owner=User.valid_objects.get(username='admin'))
        User.objects.create(username='employee')
        self.client.json_patch(reverse('siteapi:dept_child_user', args=(org1.dept.uid, )),
                               data={
                                   'subject': 'add',
                                   'user_uids': ['employee']
                               })
        self.client.json_patch(reverse('siteapi:group_child_user', args=(org2.group.uid, )),
                               data={
                                   'subject': 'add',
                                   'user_uids': ['employee']
                               })
        res = self.client.get(reverse('siteapi:org_user_detail', args=(
            org1.oid,
            'employee',
        )))
        # expect = {
        #     'user': {
        #         'username':
        #         'employee',
        #         'name':
        #         '',
        #         'mobile':
        #         '',
        #         'gender':
        #         0,
        #         'avatar':
        #         '',
        #         'private_email':
        #         '',
        #         'is_settled':
        #         False,
        #         'is_manager':
        #         False,
        #         'is_admin':
        #         False,
        #         'origin_verbose':
        #         '脚本添加',
        #         'nodes': [
        #             {
        #                 'node_uid': org2.group.node_uid,
        #                 'node_subject': 'org',
        #                 'uid': str(org2.group.uid),
        #                 'name': 'org2',
        #                 'remark': '',
        #                 'accept_user': True
        #             },
        #             {
        #                 'node_uid': org1.dept.node_uid,
        #                 'node_subject': 'dept',    # TODO@saas node subject & top for dept
        #                 'uid': str(org1.dept.uid),
        #                 'name': 'org1',
        #                 'remark': ''
        #             }
        #         ],
        #         'created':
        #         self.now_str,
        #         'last_active_time':
        #         None,
        #         'is_extern_user':
        #         False,
        #         'require_reset_password':
        #         False,
        #         'has_password':
        #         False
        #     },
        #     'employee_number': '',
        #     'position': '',
        #     'hiredate': None,
        #     'remark': '',
        #     'email': '',
        # }
        expect1 = {
            'username': 'employee',
            'name': '',
            'mobile': '',
            'gender': 0,
            'avatar': '',
            'private_email': '',
            'is_settled': False,
            'is_manager': False,
            'is_admin': False,
            'origin_verbose': '脚本添加',
            'created': self.now_str,
            'last_active_time': None,
            'is_extern_user': False,
            'require_reset_password': False,
            'has_password': False,
            'employee_number': '',
            'position': '',
            'hiredate': None,
            'remark': '',
            'email': '',
        }
        self.assertEqual(expect1, res.json())
        # res = self.client.json_patch(reverse('siteapi:org_user_detail', args=(org1.oid, 'employee')),
        #                              data={
        #                                  'remark': 'remark1',
        #                                  'position': 'position1',
        #                                  'email': 'email1',
        #                              }).json()
        # del res['user']
        # expect = {
        #     'employee_number': '',
        #     'position': 'position1',
        #     'hiredate': None,
        #     'remark': 'remark1',
        #     'email': 'email1'
        # }
        # self.assertEqual(expect, res)
        # res = self.client.get(reverse('siteapi:org_user_detail', args=(org1.oid, 'employee'))).json()
        # del res['user']
        # self.assertEqual(expect, res)

        self.client.json_patch(reverse('siteapi:org_user_detail', args=(org2.oid, 'employee')),
                               data={
                                   'position': 'position2',
                                   'employee_number': '123',
                               })
        # expect_ = {'employee_number': '123', 'position': 'position2', 'hiredate': None, 'remark': '', 'email': ''}
        # res = self.client.get(reverse('siteapi:org_user_detail', args=(org2.oid, 'employee'))).json()
        # del res['user']
        # self.assertEqual(expect_, res)
        # res = self.client.get(reverse('siteapi:org_user_detail', args=(org1.oid, 'employee'))).json()
        # del res['user']
        # self.assertEqual(expect, res)

    def test_create_user(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)
        res = res.json()
        res['user'].pop('nodes')

        self.assertEqual(res, EMPLOYEE)

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
                                            'mobile': '18812345678',
                                            'gender': 2,
                                            'password': 'password',
                                            'avatar': '',
                                        },
                                    })
        res = self.anonymous.json_post(reverse('siteapi:user_login'),
                                       data={
                                           'username': 'employee2',
                                           'password': 'password'
                                       })
        self.assertEqual(res.status_code, 200)

    def test_username_unique(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)
        res = self.create_user()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['existed']})

    def test_get_user(self):
        self.create_user()
        res = self.client.get(reverse('siteapi:user_detail', args=('employee1', ))).json()
        res['user'].pop('nodes')
        self.assertEqual(res, EMPLOYEE)

    def test_delete_user(self):
        self.create_user()

        res = self.client.delete(reverse('siteapi:user_detail', args=('employee1', )))
        self.assertEqual(res.status_code, 204)

        res = self.client.get(reverse('siteapi:user_detail', args=('employee1', )))

        self.assertEqual(res.status_code, 404)

    def test_update_user(self):
        self.create_user()
        org = Org.create(name='org1', owner=User.objects.get(username='admin'))
        cf = CustomField.valid_objects.create(org=org, name='忌口')    # pylint:disable=invalid-name
        patch_data = {
            'username': 'employee1',
            'name': 'new_employee1',
            'mobile': '18812345678',
            'gender': 2,
            'is_settled': False,
            'private_email': 'private_email',
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
        }

        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual(res.status_code, 200)
        res = res.json()
        expect = {
            'username': 'employee1',
            'avatar': '',
            'created': self.now_str,
            'last_active_time': None,
            'name': 'new_employee1',
            'mobile': '18812345678',
            'private_email': 'private_email',
            'is_settled': False,
            'is_manager': False,
            'is_admin': False,
            'is_extern_user': False,
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
                'pretty': [
        # {
        # 'uuid': cf.uuid.hex, Deprecated TODO@saas
        # 'name': '忌口',
        # 'value': '无'
        # }
                ]
            },
            'require_reset_password': False,
            'has_password': False,
        }
        res['user'].pop('nodes')
        self.assertEqual(expect, res['user'])

    def test_wechat_user(self):
        self.create_user()
        user = User.valid_objects.get(username='employee1')

        # bound
        patch_data = {'wechat_user': {'unionid': 'unionid-1'}}
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual("unionid-1", res.json()['user']['wechat_user']['unionid'])
        self.assertEqual(1, WechatUser.objects.filter(user=user).count())

        # update
        patch_data = {'wechat_user': {'unionid': 'unionid-2'}}
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual("unionid-2", res.json()['user']['wechat_user']['unionid'])

        # unbound
        patch_data = {
            'wechat_user': None,
        }
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual(0, WechatUser.objects.filter(user=user).count())
        self.assertNotIn("wechat_user", res.json()['user'])

        patch_data = {
            'wechat_user': None,
        }
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual(res.status_code, 200)

    def test_get_user_group(self):
        self.create_user()
        res = self.client.get(reverse('siteapi:user_group', args=('employee1', )))
        expect = {
            'groups': [{
                'uid': 'root',
                'node_uid': 'g_root',
                'node_subject': 'root',
                'name': 'root',
                'remark': '所有顶级的组的父级，可视为整个公司。请勿修改',
                'accept_user': False
            }]
        }
        self.assertEqual(res.json(), expect)

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

    def test_reset_user_password(self):
        employee = User.objects.create(username='test_reset_pwd')

        res = self.client.json_patch(reverse('siteapi:user_password', args=(employee.username, )),
                                     data={
                                         'password': 'complicated_password_',
                                         'require_reset_password': False
                                     })
        expect = {'require_reset_password': False}
        self.assertEqual(expect, res.json())
        res = self.anonymous.json_post(reverse('siteapi:user_login'),
                                       data={
                                           'username': employee.username,
                                           'password': 'complicated_password_'
                                       })
        self.assertFalse(res.json()['require_reset_password'])

        res = self.client.json_patch(reverse('siteapi:user_password', args=(employee.username, )),
                                     data={
                                         'password': 'reset_password',
                                         'require_reset_password': True
                                     })
        expect = {'require_reset_password': True}
        self.assertEqual(expect, res.json())
        res = self.anonymous.json_post(reverse('siteapi:user_login'),
                                       data={
                                           'username': employee.username,
                                           'password': 'reset_password'
                                       })
        self.assertTrue(res.json()['require_reset_password'])
        client = self.login(employee.username, 'reset_password')
        res = client.json_patch(reverse('siteapi:ucenter_password'),
                                data={
                                    'username': employee.username,
                                    'old_password': 'reset_password',
                                    'new_password': 'new_password'
                                })
        self.assertFalse(User.objects.get(username='test_reset_pwd').require_reset_password)

    def test_create_invalid_username(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)
        res = res.json()
        res['user'].pop('nodes')

        User.valid_objects.get(username=USER_DATA['username']).delete()
        res = self.client.json_post(reverse('siteapi:user_list'),
                                    data={
                                        'group_uids': ['root'],
                                        'dept_uids': ['none'],
                                        'user': {
                                            'username': '123',
                                            'mobile': '13838383838'
                                        },
                                    })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'username': ['invalid']})


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
