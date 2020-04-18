'''
tests for user convert
'''
# pylint: disable=missing-docstring

from django.urls import reverse

from ....siteapi.v1.tests import TestCase
from ....siteapi.v1.tests.test_user import USER_DATA
from ....oneid_meta.models import Dept, Group, User


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

        self.client.json_patch(reverse('siteapi:user_convert_to_intra', args=(USER_DATA['username'], )),
                               data={
                                   'name': 'new_name',
                                   'hiredate': '2019-06-04T09:01:44+08:00',
                               })
        user = User.valid_objects.get(username=USER_DATA['username'])
        self.assertTrue(user.is_intra)
        self.assertEqual(user.name, 'new_name')

    def test_convert_intra_to_extern(self):
        self.create_intra_user()

        res = self.client.json_patch(reverse('siteapi:user_convert_to_extern', args=(USER_DATA['username'], )),
                                     data={'name': 'new_name'})
        user = User.valid_objects.get(username=USER_DATA['username'])
        self.assertFalse(user.is_intra)
        self.assertEqual(user.name, 'new_name')

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
