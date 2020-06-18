'''
tests for api abort org
'''

# pylint: disable=missing-docstring, invalid-name, too-many-locals, too-many-statements

import uuid
from unittest import mock

from django.urls import reverse
from oneid_meta.models import User, Org

from siteapi.v1.tests import TestCase

ORG_DATA = [
    {
        'name': '组织1'
    },
    {
        'name': '组织2'
    },
]

ILL_FORMED_DATA = {'name2': '组织3'}


class OrgTestCase(TestCase):
    def setUp(self):
        super(OrgTestCase, self).setUp()
        self.admin = User.valid_objects.get(username='admin')
        self.org_1 = Org.create(name='org_1', owner=self.admin)

        self.user = User.create_user('u1', 'u1')
        self.client = self.login_as(self.user)

        self.org_1.add_member(self.user)
        self.user.switch_org(self.org_1)

        self.org_2 = Org.create(name='org_2', owner=self.user)
        self.org_2.add_member(self.user)

    def test_org_list(self):
        res = self.client.get(reverse('siteapi:org_list'))
        actual = [{
            'name': item['name'],
            'role': item['role'],
        } for item in res.json()]
        expect = [
            {
                'name': 'org_1',
                'role': 'member'
            },
            {
                'name': 'org_2',
                'role': 'owner'
            },
        ]
        self.assertEqual(actual, expect)

        res = self.client.get(reverse('siteapi:org_list'), data={'role': 'owner'})
        actual = [{
            'name': item['name'],
            'role': item['role'],
        } for item in res.json()]
        expect = [
            {
                'name': 'org_2',
                'role': 'owner'
            },
        ]
        self.assertEqual(actual, expect)

    def test_create_org(self):
        res = self.client.post(reverse('siteapi:org_list'), data={
            'name': 'org_3',
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['name'], 'org_3')

    def test_org_detail(self):
        # 查看自己的组织
        res = self.client.get(reverse('siteapi:org_detail', args=(self.org_2.uuid.hex, )))
        self.assertEqual(res.json()['name'], 'org_2')

        # 管理自己的组织
        res = self.client.json_patch(reverse('siteapi:org_detail', args=(self.org_2.uuid.hex, )),
                                     data={
                                         'name': 'new_name',
                                     })
        self.assertEqual(res.json()['name'], 'new_name')

        # 查看自己所属组织
        res = self.client.get(reverse('siteapi:org_detail', args=(self.org_1.uuid.hex, )))
        self.assertEqual(res.json()['name'], 'org_1')

        # 管理他人的组织
        res = self.client.json_patch(reverse('siteapi:org_detail', args=(self.org_1.uuid.hex, )),
                                     data={
                                         'name': 'new_name',
                                     })
        self.assertEqual(res.status_code, 403)
        res = self.client.delete(reverse('siteapi:org_detail', args=(self.org_1.uuid.hex, )))
        self.assertEqual(res.status_code, 403)

    def test_delete_org(self):
        res = self.client.get(reverse('siteapi:org_list'))
        self.assertEqual(2, len(res.json()))

        res = self.client.delete(reverse('siteapi:org_detail', args=(self.org_2.uuid.hex, )))
        self.assertEqual(res.status_code, 204)

        res = self.client.get(reverse('siteapi:org_list'))
        self.assertEqual(1, len(res.json()))

    def test_ucenter_org(self):
        # u1 is in org_2 after creating org_2 in setup()
        res = self.client.get(reverse('siteapi:ucenter_org'))
        self.assertEqual(res.json()['name'], 'org_2')
        self.assertEqual(res.json()['role'], 'owner')

        # switch org
        res = self.client.put(reverse('siteapi:ucenter_org'), data={'oid': self.org_1.uuid})
        self.assertEqual(res.json()['name'], 'org_1')
        self.assertEqual(res.json()['role'], 'member')

        self.client.post(reverse('siteapi:org_list'), data={
            'name': 'org_2',
        })
        res = self.client.get(reverse('siteapi:ucenter_org'))
        self.assertEqual(res.json()['name'], 'org_2')
        self.assertEqual(res.json()['role'], 'owner')

        # switch org
        self.client.json_put(reverse('siteapi:ucenter_org'), data={
            'oid': str(self.org_1.uuid),
        })
        res = self.client.get(reverse('siteapi:ucenter_org'))
        self.assertEqual(res.json()['name'], 'org_1')


class OrgMemberTestCase(TestCase):
    def setUp(self):
        super(OrgMemberTestCase, self).setUp()
        self.admin = User.valid_objects.get(username='admin')
        self.org_1 = Org.create(name='org_1', owner=self.admin)

        self.user = User.create_user('u1', 'u1')
        self.user2 = None
        self.client = self.login_as(self.user)

        self.org_1.add_member(self.user)
        self.user.switch_org(self.org_1)

        self.org_2 = Org.create(name='org_2', owner=self.user)
        self.org_2.add_member(self.user)

        self.client = self.login_as(self.user)

    def test_get_org_members(self):
        res = self.client.get(reverse('siteapi:org_user_list', args=(self.org_2.uuid.hex, )))
        self.assertEqual(res.json()['count'], 1)
        self.assertEqual(len(res.json()['results']), 1)
        self.assertEqual(res.json()['results'][0]['username'], 'u1')

        res = self.client.get(reverse('siteapi:org_user_list', args=(self.org_2.uuid.hex, )), data={'page': 2})
        self.assertEqual(res.status_code, 404)

    def test_manager_members(self):
        url = reverse('siteapi:org_user_list', args=(self.org_2.uuid.hex, ))

        self.assertEqual(self.client.get(url).json()['count'], 1)

        res = self.client.json_patch(url, data={
            'subject': 'add',
            'usernames': ['admin11'],
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.json_patch(url, data={
            'subject': 'add',
            'usernames': ['admin'],
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get(url).json()['count'], 2)

        res = self.client.json_patch(url, data={
            'subject': 'delete',
            'usernames': ['admin'],
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get(url).json()['count'], 1)

        res = self.client.json_patch(
            url,
            data={
                'subject': 'delete',
                'usernames': ['u1'],    # try to delete owner
            })
        self.assertEqual(res.status_code, 400)

    def test_edit_member(self):
        url = reverse('siteapi:org_user_detail', args=(self.org_2.uuid.hex, self.user.username))
        res = self.client.get(url)
        expect = {'username': 'u1', 'email': ''}
        self.assertEqualScoped(res.json(), expect, keys=['username', 'email'])

        res = self.client.json_patch(url, data={'email': 'new_email'})
        expect = {'username': 'u1', 'email': 'new_email'}
        self.assertEqualScoped(res.json(), expect, keys=['username', 'email'])

    def test_get_org_member_node_list(self):
        # 向组中添加测试用户
        self.user2 = User.create_user('u2', 'u2')
        self.org_2.add_member(self.user2)
        res = self.client.get(reverse('siteapi:group_child_group', args=(self.org_2.group.uid, )))
        child_group = res.json()['groups'].pop()
        data = '{0}"user_uids": ["u2"], "group_uids": ["{1}"], "subject": "add"{2}'.format('{', child_group['uid'], '}')
        self.client.patch(reverse('siteapi:group_child_user', args=(self.org_2.group.uid, )),
                          data=data,
                          content_type='application/json;charset=utf-8')
        # 获取测试用户在组织中所属节点的信息
        res = self.client.get(reverse('siteapi:org_user_node_detail', args=(
            self.org_2.uuid,
            'u2',
        )))
        self.assertEqual(res.json()['nodes'][0]['name'], 'org_2')
        self.client = self.login_as(self.admin)
        res = self.client.get(reverse('siteapi:org_user_node_detail', args=(
            self.org_2.uuid,
            'u2',
        )))
        self.assertEqual(res.status_code, 403)


class OrgInvitationTestCase(TestCase):
    def setUp(self):
        super(OrgInvitationTestCase, self).setUp()

        self.owner = User.create_user('owner', 'owner')
        self.org = Org.create(name='org', owner=self.owner)

        self.new_user = User.create_user('u1', 'u1')

    @mock.patch('siteapi.v1.views.org.redis_conn.get')
    @mock.patch('siteapi.v1.views.org.redis_conn.set')
    def test_invitation_link(self, _, mock_redis_get):
        # 获取邀请key
        mock_redis_get.return_value = None
        self.client = self.login_as(self.owner)
        res = self.client.get(reverse('siteapi:org_invite_link', args=(self.org.oid_str, )))
        self.assertEqual(res.status_code, 200)
        self.assertIn('invite_link_key', res.json())
        key = res.json()['invite_link_key']

        # 刷新
        res = self.client.json_put(reverse('siteapi:org_invite_link', args=(self.org.oid_str, )))
        self.assertEqual(res.status_code, 200)
        self.assertIn('invite_link_key', res.json())
        self.assertNotEqual(res.json()['invite_link_key'], key)
        key = res.json()['invite_link_key']

        # 查看
        client = self.login_as(self.new_user)
        mock_redis_get.return_value = key
        res = client.get(reverse('siteapi:org_invite_link_detail', args=(self.org.oid_str, key)))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['oid'], self.org.oid_str)
        self.assertEqual(res.json()['role'], '')

        res = client.get(reverse('siteapi:org_invite_link_detail', args=(str(uuid.uuid4()), key)))
        self.assertEqual(res.status_code, 404)

        # 加入
        res = client.json_post(reverse('siteapi:org_invite_link_detail', args=(self.org.oid_str, key)))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['role'], 'member')
