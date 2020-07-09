'''
tests for api about user
'''
# pylint: disable=missing-docstring, too-many-lines
import json
import time
import unittest
import random
from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (DingUser, PosixUser, Group, Dept, User, CustomField, DeptMember, Perm, UserPerm,
                               WechatUser, QQUser, AlipayUser)

EMPLOYEE = {
    'user_id':
    2,
    'avatar':
    '',
    'username':
    'employee1',
    'name':
    'employee1',
    'email':
    'email',
    'mobile':
    '18812345678',
    'employee_number':
    '',
    'gender':
    2,
    'private_email':
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
    '管理员添加',
    'position':
    '',
    'hiredate':
    None,
    'remark':
    '',
    'last_active_time':
    None,
    'created':
    TestCase.now_str,
    'require_reset_password':
    False,
    'has_password':
    False,
    'ding_user': {
        'uid': 'ding_employee2',
        'account': '18812345678',
        'data': '{"key": "val"}'
    },
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

SKIP_GET_USER_LIST__CUSTOM = True


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
        '''搜索用户列表'''
        self.create_user()
        client = self.client
        res = client.get(reverse('siteapi:user_list'), data={'keyword': '188'})
        user_list = res.json()['results']
        expect_count = 1
        self.assertEqual(expect_count, len(user_list))

        res = client.get(reverse('siteapi:user_list'), data={'username': 'employee1'})
        self.assertEqual(1, len(res.json()['results']))
        res = client.get(reverse('siteapi:user_list'), data={'username': 'employee'})
        self.assertEqual(0, len(res.json()['results']))

        res = client.get(reverse('siteapi:user_list'), data={'name': 'employee1'})
        self.assertEqual(1, len(res.json()['results']))
        res = client.get(reverse('siteapi:user_list'), data={'name': 'employee'})
        self.assertEqual(0, len(res.json()['results']))

        res = client.get(reverse('siteapi:user_list'),
                         data={
                             'name__icontains': 'ployee1',
                             'created__lte': '1800-01-01T08:00:00+08:00'
                         })
        self.assertEqual(0, len(res.json()['results']))
        res = client.get(reverse('siteapi:user_list'),
                         data={
                             'name__icontains': 'ployee1',
                             'created__gte': '1800-01-01T08:00:00+08:00'
                         })
        self.assertEqual(1, len(res.json()['results']))

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
                'user_id': 2,
                'created': self.now_str,
                'username': 'employee',
                'name': '',
                'email': '',
                'mobile': '',
                'employee_number': '',
                'last_active_time': None,
                'gender': 0,
                'avatar': '',
                'private_email': '',
                'nodes': [],
                'position': '',
                'is_settled': False,
                'is_manager': False,
                'is_admin': False,
                'is_extern_user': False,
                'origin_verbose': '脚本添加',
                'hiredate': None,
                'remark': '',
                'require_reset_password': False,
                'has_password': False,
            }]
        }
        self.assertEqual(res.json(), expect)

    @unittest.skipIf(SKIP_GET_USER_LIST__CUSTOM, '使用mysql对接测试')
    def test_get_user_list__custom(self):
        """测试用户自定义字段检索"""
        user1_data = {
            'username': 'employee1',
            'name': 'employee1',
            'avatar': '',
            'email': 'email1',
            'mobile': '18812345678',
            'private_email': '',
            'position': '',
            'gender': 2,
            'custom_user': {
                'data': {
                    'age': '18',
                    'is_person': 'true',
                    'sex': 'male'
                }
            }
        }
        self.client.json_post(reverse('siteapi:user_list'),
                              data={
                                  'group_uids': ['root'],
                                  'dept_uids': ['root'],
                                  'user': user1_data,
                              }).json()
        user2_data = {
            'username': 'employee2',
            'name': 'employee2',
            'avatar': '',
            'email': 'email2',
            'mobile': '18812345670',
            'private_email': '',
            'position': '',
            'gender': 2,
            'custom_user': {
                'data': {
                    'age': '19',
                    'is_person': 'true',
                    'sex': 'female'
                }
            }
        }
        self.client.json_post(reverse('siteapi:user_list'),
                              data={
                                  'group_uids': ['root'],
                                  'dept_uids': ['root'],
                                  'user': user2_data,
                              }).json()

        # 测试精确查找（equal）
        res = self.client.get(reverse('siteapi:user_list'), {'sex__custom': 'male'})
        self.assertEqual(res.json()['count'], 1)
        # 测试范围搜索（lte, gte, lt, gt)
        res = self.client.get(reverse('siteapi:user_list'), {'age__lte__custom': "18"})
        self.assertEqual(res.json()['count'], 1)
        res = self.client.get(reverse('siteapi:user_list'), {'age__gte__custom': 19})
        self.assertEqual(res.json()['count'], 1)
        res = self.client.get(reverse('siteapi:user_list'), {'age__gt__custom': 18})
        self.assertEqual(res.json()['count'], 1)
        res = self.client.get(reverse('siteapi:user_list'), {'age__lt__custom': 19})
        self.assertEqual(res.json()['count'], 1)

    # pylint:disable=too-many-locals
    # pylint:disable=invalid-name
    # pylint:disable=too-many-statements
    def test_advanced_search_user(self):    # pylint:disable=too-many-locals
        """测试获取用户列表的高级搜索形式"""
        # 创建测试用户对象
        u1_data = {
            'username': 'employee1',
            'name': 'employee1',
            'avatar': '',
            'email': 'email1',
            'mobile': '18612345678',
            'private_email': '',
            'position': '',
            'gender': 2,
        }
        u2_data = {
            'username': 'employee2',
            'name': 'employee2',
            'avatar': '',
            'email': 'email2',
            'mobile': '18712345678',
            'private_email': '',
            'position': '',
            'gender': 2,
        }
        u3_data = {
            'username': 'employee3',
            'name': 'employee3',
            'avatar': '',
            'email': 'email3',
            'mobile': '18812345678',
            'private_email': '',
            'position': '',
            'gender': 2,
        }
        u1 = self.client.json_post(reverse('siteapi:user_list'),
                                   data={
                                       'group_uids': ['root'],
                                       'dept_uids': ['root'],
                                       'user': u1_data,
                                   }).json()
        u2 = self.client.json_post(reverse('siteapi:user_list'),
                                   data={
                                       'group_uids': ['root'],
                                       'dept_uids': ['root'],
                                       'user': u2_data,
                                   }).json()
        u3 = self.client.json_post(reverse('siteapi:user_list'),
                                   data={
                                       'group_uids': ['root'],
                                       'dept_uids': ['root'],
                                       'user': u3_data,
                                   }).json()
        # 测试通过关联账号搜索
        #  1）测试是否关联微信搜索
        _random_user = random.choice(['employee1', 'employee2', 'employee3'])
        _ = WechatUser.objects.create(unionid='unionid', user=User.valid_objects.get(username=_random_user))
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_wechat': 'false'})    # 测试已绑定微信的用户
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['username'], _random_user)
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_wechat': 'true'})    # 测试未绑定微信的用户
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertNotEqual(user['username'], _random_user)
        #  2）测试是否关联钉钉搜索
        _random_user = random.choice(['employee1', 'employee2', 'employee3'])
        _ = DingUser.objects.create(account='',
                                    uid='',
                                    data='',
                                    ding_id='',
                                    open_id='',
                                    union_id='',
                                    user=User.valid_objects.get(username=_random_user))
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_ding': 'false'})    # 测试已绑定钉钉的用户
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['username'], _random_user)
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_ding': 'true'})    # 测试未绑定钉钉的用户
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertNotEqual(user['username'], _random_user)
        #  3）测试是否关联支付宝搜索
        _random_user = random.choice(['employee1', 'employee2', 'employee3'])
        _ = AlipayUser.objects.create(alipay_user_id='', user=User.valid_objects.get(username=_random_user))
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_alipay': 'false'})    # 测试已绑定支付宝的用户
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['username'], _random_user)
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_alipay': 'true'})    # 测试未绑定支付宝的用户
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertNotEqual(user['username'], _random_user)
        #  4）测试是否关联QQ搜索
        _random_user = random.choice(['employee1', 'employee2', 'employee3'])
        _ = QQUser.objects.create(open_id='', user=User.valid_objects.get(username=_random_user))
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_qq': 'false'})    # 测试已绑定QQ的用户
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(res.json()['results'][0]['username'], _random_user)
        res = self.client.get(reverse('siteapi:user_list'), {'unbound_qq': 'true'})    # 测试未绑定QQ的用户
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertNotEqual(user['username'], _random_user)
        # 测试通过 user ids 搜索
        _random_users = random.sample([str(u1['user_id']), str(u2['user_id']), str(u3['user_id'])], 2)
        res = self.client.get(reverse('siteapi:user_list'), {'user_ids': ' '.join(_random_users)})
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertIn(str(user['user_id']), _random_users)
        # 测试通过 group uids 搜索
        _random_users = random.sample(['employee1', 'employee2', 'employee3'], 2)
        self.client.json_post(reverse('siteapi:group_child_group', args=('root', )),
                              data={
                                  'uid': 'group-test',
                                  'name': 'group-test'
                              })
        self.client.json_patch(reverse('siteapi:group_child_user', args=('group-test', )),
                               data={
                                   'user_uids': _random_users,
                                   'subject': 'add'
                               })
        # 1) 测试属于组的用户搜索
        res = self.client.get(reverse('siteapi:user_list'), {'group_uids': 'group-test'})
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertIn(user['username'], _random_users)
        # 2) 测试不属于组的用户搜索
        res = self.client.get(reverse('siteapi:user_list'), {'-group_uids': 'group-test'})
        self.assertEqual(res.json()['count'], 1)
        self.assertNotIn(res.json()['results'][0]['username'], _random_users)
        # 测试通过 perm uids 搜索
        _random_users = random.sample(['employee1', 'employee2', 'employee3'], 2)
        for username in _random_users:
            _user_perm = UserPerm.objects.get(perm=Perm.valid_objects.get(uid='system_oneid_all'),
                                              owner=User.valid_objects.get(username=username))
            _user_perm.value = True
            _user_perm.save()
        # 1) 测试拥有权限的用户搜索
        res = self.client.get(reverse('siteapi:user_list'), {'perm_uids': 'system_oneid_all'})
        self.assertEqual(res.json()['count'], 2)
        for user in res.json()['results']:
            self.assertIn(user['username'], _random_users)
        # 2) 测试未拥有权限的用户搜索
        res = self.client.get(reverse('siteapi:user_list'), {'-perm_uids': 'system_oneid_all'})
        self.assertEqual(res.json()['count'], 1)
        self.assertNotIn(res.json()['results'][0]['username'], _random_users)
        # 测试通过 sort 获取指定排序搜索
        _random_users = ['employee1', 'employee2', 'employee3']
        random.shuffle(_random_users)
        _random_times = []
        for username in _random_users:
            user = User.valid_objects.get(username=username)
            user.created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            user.save()
            timestamp = int(time.mktime(time.strptime(user.created, "%Y-%m-%d %H:%M:%S")))
            _random_times.append(timestamp)
            time.sleep(1)
        # 1) 测试按照注册时间排序搜索
        res = self.client.get(reverse('siteapi:user_list'), {'sort': 'created'})
        for i in range(0, len(res.json()['results'])):
            timestamp = int(time.mktime(time.strptime(res.json()['results'][i]['created'], "%Y-%m-%dT%H:%M:%S+08:00")))
            self.assertEqual(timestamp, _random_times[i])
        # 2) 测试按照user id逆序搜索
        res = self.client.get(reverse('siteapi:user_list'), {'sort': '-id'})
        for i in range(0, 3):
            self.assertEqual(res.json()['results'][i]['user_id'], 4 - i)

    def test_create_user(self):
        res = self.create_user()
        self.assertEqual(res.status_code, 201)
        res = res.json()

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
                                            'email': 'email',
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
        self.assertEqual(res, EMPLOYEE)

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
        res = res.json()
        expect = {
            'user_id': 2,
            'username': 'employee1',
            'avatar': '',
            'created': self.now_str,
            'last_active_time': None,
            'name': 'new_employee1',
            'email': 'new_email',
            'mobile': '18812345678',
            'employee_number': '',
            'private_email': 'private_email',
            'position': 'position',
            'is_settled': False,
            'is_manager': False,
            'is_admin': False,
            'is_extern_user': False,
            'origin_verbose': '管理员添加',
            'gender': 2,
            'remark': '',
            'ding_user': {
                'uid': 'ding_employee2',
                'account': '18812345678',
                'data': '{"key": "new_val"}'
            },
        # 'posix_user': {
        #     'uid': 500,
        #     'gid': 500,
        #     'pub_key': '',
        #     'home': ''
        # },
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
            'require_reset_password': False,
            'has_password': False,
        }
        self.assertEqual(expect, res)

    def test_wechat_user(self):
        self.create_user()
        user = User.valid_objects.get(username='employee1')

        # bound
        patch_data = {'wechat_user': {'unionid': 'unionid-1'}}
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual("unionid-1", res.json()['wechat_user']['unionid'])
        self.assertEqual(1, WechatUser.objects.filter(user=user).count())

        # update
        patch_data = {'wechat_user': {'unionid': 'unionid-2'}}
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual("unionid-2", res.json()['wechat_user']['unionid'])

        # unbound
        patch_data = {
            'wechat_user': None,
        }
        res = self.client.json_patch(reverse('siteapi:user_detail', args=('employee1', )), patch_data)
        self.assertEqual(0, WechatUser.objects.filter(user=user).count())
        self.assertNotIn("wechat_user", res.json())

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
        res.pop('nodes')

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
