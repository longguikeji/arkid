'''
tests for user convert
'''
# pylint: disable=missing-docstring

from django.urls import reverse

from siteapi.v1.tests import TestCase
from siteapi.v1.tests.test_user import USER_DATA
from oneid_meta.models import Dept, Group, User


class UserConvertTestCase(TestCase):
    def setUp(self):
        super().setUp()
        root, _ = Group.objects.get_or_create(uid='root')
        group, _ = Group.objects.get_or_create(uid='extern', parent=root, name='外部联系人')
        group.save()

        Dept.objects.create(name='dept', uid='dept')
        extern = Group.objects.get(uid='extern')
        Group.objects.create(parent=extern, uid='label1', name='label1')

    def create_extern_user(self):
        self.client.json_post(reverse('siteapi:user_list'), data={
            'group_uids': ['extern'],
            'user': USER_DATA,
        })

    def create_intra_user(self):
        self.client.json_post(reverse('siteapi:user_list'), data={
            'dept_uids': ['dept'],
            'user': USER_DATA,
        })

    def test_convert_extern_to_intra(self):
        self.create_extern_user()

        res = self.client.json_patch(reverse('siteapi:user_convert_to_intra', args=(USER_DATA['username'], )),
                                     data={
                                         'node_uid': 'd_dept',
                                         'name': 'new_name',
                                         'hiredate': '2019-06-04T09:01:44+08:00',
                                     })
        expect = {
            'user': {
                'user_id': 2,
                'username': 'employee1',
                'name': 'new_name',
                'email': 'email',
                'mobile': '18812345678',
                'employee_number': '',
                'gender': 2,
                'avatar': '',
                'private_email': '',
                'position': '',
                'hiredate': '2019-06-04T09:01:44+08:00',
                'remark': '',
                'ding_user': {
                    'uid': 'ding_employee2',
                    'account': '18812345678',
                    'data': '{"key": "val"}'
                },
                'is_settled': False,
                'is_manager': False,
                'is_admin': False,
                'origin_verbose': '管理员添加'
            },
            'groups': [],
            'depts': [{
                'dept_id': 2,
                'node_uid': 'd_dept',
                'node_subject': 'dept',
                'uid': 'dept',
                'name': 'dept',
                'remark': ''
            }],
            'nodes': [{
                'dept_id': 2,
                'node_uid': 'd_dept',
                'node_subject': 'dept',
                'uid': 'dept',
                'name': 'dept',
                'remark': ''
            }]
        }
        self.assertEqual(expect, res.json())

    def test_convert_intra_to_extern(self):
        self.create_intra_user()

        res = self.client.json_patch(reverse('siteapi:user_convert_to_extern', args=(USER_DATA['username'], )),
                                     data={
                                         'node_uid': 'd_dept',
                                         'name': 'new_name'
                                     })
        expect = {
            'user': {
                'user_id': 2,
                'username': 'employee1',
                'name': 'new_name',
                'email': 'email',
                'mobile': '18812345678',
                'employee_number': '',
                'gender': 2,
                'avatar': '',
                'private_email': '',
                'position': '',
                'ding_user': {
                    'uid': 'ding_employee2',
                    'account': '18812345678',
                    'data': '{"key": "val"}'
                },
                'is_settled': False,
                'is_manager': False,
                'is_admin': False,
                'origin_verbose': '管理员添加',
                'hiredate': None,
                'remark': '',
            },
            'groups': [{
                'group_id': 2,
                'node_uid': 'g_extern',
                'node_subject': 'root',
                'uid': 'extern',
                'name': '外部联系人',
                'remark': '',
                'accept_user': True
            }],
            'depts': [],
            'nodes': []
        }
        self.assertEqual(expect, res.json())

        res = self.client.json_patch(reverse('siteapi:user_node', args=(USER_DATA['username'], )),
                                     data={
                                         "node_uids": ['g_label1'],
                                         "subject": 'override',
                                     })
        expect = {
            'nodes': [{
                'group_id': 2,
                'node_uid': 'g_extern',
                'node_subject': 'root',
                'uid': 'extern',
                'name': '外部联系人',
                'remark': '',
                'accept_user': True
            }, {
                'group_id': 3,
                'node_uid': 'g_label1',
                'node_subject': 'root',
                'uid': 'label1',
                'name': 'label1',
                'remark': '',
                'accept_user': True
            }]
        }
        self.assertEqual(expect, res.json())
        self.assertFalse(User.objects.get(username=USER_DATA['username']).is_intra)
