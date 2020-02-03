# pylint: disable=missing-docstring
'''
test for api about node
'''
from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    Dept,
    DeptMember,
    Group,
    GroupMember,
    User,
    Org,
    Perm,
    DeptPerm,
    GroupPerm,
)
from oneid_meta.models.mixin import TreeNode as Node


def create_node_tree(cls, trees):
    '''
    根据树的描述进行创建
    '''
    for uid, sub_trees in trees.items():
        node = cls.objects.create(uid=uid, name=uid)

        for sub_node in create_node_tree(cls, sub_trees):
            if not sub_node.parent:
                sub_node.parent = node
                sub_node.save()
            yield sub_node
        yield node


class NodeTestCase(TestCase):
    def setUp(self):
        super().setUp()

        owner = User.create_user('owner', 'owner')
        self.owner = self.login_as(owner)
        self._owner = owner
        self.org = Org.create(name='org', owner=owner)

        root = self.org.dept
        level_1 = Dept.valid_objects.create(uid='level_1', name='level_1', parent=root)
        Dept.valid_objects.create(uid='level_2-1', name='level_2-1', parent=level_1, order_no=2)
        Dept.valid_objects.create(uid='level_2-2', name='level_2-2', parent=level_1, order_no=1)
        user = User.create_user('employee', 'employee')
        DeptMember.valid_objects.create(user=user, owner=root)
        user = User.create_user('employee_2', 'employee_2')

        root = self.org.group
        role_group = Group.valid_objects.create(uid='role_group_1', name='role_group_1', parent=root, accept_user=False)
        role_1 = Group.valid_objects.create(uid='role_1', name='role_1', parent=role_group, order_no=2)
        Group.valid_objects.create(uid='role_2', name='role_2', parent=role_group, order_no=1)
        GroupMember.valid_objects.create(user=user, owner=role_1)

    def test_get_node_detail(self):
        res = self.client.get(reverse('siteapi:node_detail', args=('d_level_1', )))
        expect = {
            'parent_uid': str(self.org.dept.uid),
            'parent_node_uid': self.org.dept.node_uid,
            'parent_name': self.org.dept.name,
            'uid': 'level_1',
            'name': 'level_1',
            'remark': '',
            'dept_id': 3,
            'node_subject': 'dept',
            'node_uid': 'd_level_1',
            'node_scope': [],
            'user_scope': [],
            'visibility': 1
        }
        self.assertEqual(res.json(), expect)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('siteapi:node_detail', args=('g_role_group_1', )))
        expect = {
            'parent_uid': str(self.org.group.uid),
            'parent_node_uid': self.org.group.node_uid,
            'parent_name': self.org.group.name,
            'uid': 'role_group_1',
            'node_uid': 'g_role_group_1',
            'node_subject': 'root',
            'name': 'role_group_1',
            'remark': '',
            'group_id': 7,
            'accept_user': False,
            'node_scope': [],
            'user_scope': [],
            'visibility': 1
        }
        self.assertEqual(res.json(), expect)
        self.assertEqual(res.status_code, 200)

    def test_get_node_detail_with_scope(self):
        node, _ = Node.retrieve_node('d_level_1')
        node.user_scope = ['not_existed']
        node.save()

        res = self.client.get(reverse('siteapi:node_detail', args=('d_level_1', )))
        self.assertEqual([], res.json()['user_scope'])

    def test_get_node_tree(self):
        res = self.client.get(reverse('siteapi:node_tree', args=('d_level_1', )))
        expect = {
            'info': {
                'uid': 'level_1',
                'node_uid': 'd_level_1',
                'node_subject': 'dept',
                'name': 'level_1',
                'remark': '',
                'dept_id': 3
            },
            'nodes': [
                {
                    'info': {
                        'uid': 'level_2-2',
                        'node_uid': 'd_level_2-2',
                        'node_subject': 'dept',
                        'name': 'level_2-2',
                        'remark': '',
                        'dept_id': 5
                    },
                    'nodes': []
                },
                {
                    'info': {
                        'uid': 'level_2-1',
                        'node_uid': 'd_level_2-1',
                        'node_subject': 'dept',
                        'name': 'level_2-1',
                        'remark': '',
                        'dept_id': 4
                    },
                    'nodes': []
                },
            ]
        }
        self.assertEqual(res.json(), expect)

    def test_get_node_child_node(self):
        res = self.client.get(reverse('siteapi:node_child_node', args=('g_role_group_1', )))
        expect = {
            'nodes': [
                {
                    'group_id': 9,
                    'node_subject': 'root',    # TODO@saas node subject
                    'node_uid': 'g_role_2',
                    'uid': 'role_2',
                    'name': 'role_2',
                    'remark': '',
                    'accept_user': True,
                },
                {
                    'group_id': 8,
                    'node_subject': 'root',
                    'node_uid': 'g_role_1',
                    'uid': 'role_1',
                    'name': 'role_1',
                    'remark': '',
                    'accept_user': True,
                }
            ]
        }
        self.assertEqual(expect, res.json())

        Dept.valid_objects.create(uid='level_2-3', name='level_2-3')
        res = self.client.json_patch(reverse('siteapi:node_child_node', args=('d_level_1', )),
                                     data={
                                         'node_uids': ['d_level_2-3'],
                                         'subject': 'add',
                                     })
        expect = ['d_level_2-2', 'd_level_2-1', 'd_level_2-3']
        self.assertEqual(expect, [item['node_uid'] for item in res.json()['nodes']])

    def test_node_child_node_sort(self):
        dept_1 = {
            'node_uid': "",
            'name': "123",
            'node_scope': [],
            'user_scope': [],
            'manager_group': {
                'nodes': [],
                'users': [],
                'perms': [],
                'apps': [],
                'scope_subject': 1
            },
            'nodes': [],
            'perms': [],
            'apps': [],
            'scope_subject': 1,
            'users': [],
        }
        self.client.json_post(reverse('siteapi:node_child_node', args=(self.org.dept.node_uid, )), data=dept_1)

        expect = {
            'nodes': [{
                'dept_id': 3,
                'name': 'level_1',
                'node_subject': 'dept',
                'node_uid': 'd_level_1',
                'remark': '',
                'uid': 'level_1'
            }, {
                'dept_id': 6,
                'name': '123',
                'node_subject': 'dept',
                'node_uid': 'd_123',
                'remark': '',
                'uid': '123'
            }]
        }
        res = self.client.json_patch(reverse('siteapi:node_child_node', args=(self.org.dept.node_uid, )),\
            data={'node_uids':["d_level_1"], 'subject':'add'})
        self.assertEqual(res.json(), expect)

        res = self.client.json_patch(reverse('siteapi:node_child_node', args=(self.org.dept.node_uid, )),\
            data={'node_uids':["d_123"], 'subject':'add'})
        self.assertEqual(res.json(), expect)

    def test_delete_node(self):
        res = self.client.delete(reverse('siteapi:node_detail', args=('g_role_2', )))
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Group.valid_objects.filter(uid='role_2').exists())

    def test_create_user(self):
        from siteapi.v1.tests.test_user import USER_DATA    # pylint: disable=import-outside-toplevel
        res = self.client.json_post(
            reverse('siteapi:user_list'),
            data={
                'node_uids': ['d_root', 'g_root'],
                'user': USER_DATA
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(User.valid_objects.filter(username='employee1').exists())
        self.assertTrue(DeptMember.valid_objects.filter(user__username='employee1', owner__uid='root').exists())
        self.assertTrue(GroupMember.valid_objects.filter(user__username='employee1', owner__uid='root').exists())
        expect = ['g_root', 'd_root']
        self.assertEqual(expect, [item['node_uid'] for item in res.json()['nodes']])

    def test_user_node(self):
        res = self.client.get(reverse('siteapi:user_node', args=('employee', )))
        expect = [self.org.dept.node_uid]
        self.assertEqual(expect, [item['node_uid'] for item in res.json()['nodes']])

        res = self.client.json_patch(
            reverse('siteapi:user_node', args=('employee', )),
            data={
                'node_uids': [self.org.group.node_uid],
                'subject': 'add'
            },
        )
        expect = [self.org.dept.node_uid, self.org.group.node_uid]
        self.assertEqual(expect, [item['node_uid'] for item in res.json()['nodes']])

    def test_node_perm(self):
        url = reverse('siteapi:node_perm', args=('d_root', ))
        node_perm = DeptPerm.objects.create(perm=Perm.objects.get(uid='system_oneid_all'),
                                            owner=Dept.objects.get(uid='root'))
        res = self.client.get(url)
        self.assertEqual(1, res.json()['count'])

        self.assertFalse(node_perm.value)
        res = self.client.json_patch(url, data={'perm_statuses': [{'uid': 'system_oneid_all', 'status': 1}]})
        node_perm.refresh_from_db()
        self.assertTrue(node_perm.value)

        url = reverse('siteapi:node_perm', args=('g_root', ))
        node_perm = GroupPerm.objects.create(perm=Perm.objects.get(uid='system_oneid_all'),
                                             owner=Group.objects.get(uid='root'))
        res = self.client.get(url)
        self.assertEqual(1, res.json()['count'])

        self.assertFalse(node_perm.value)
        res = self.client.json_patch(url, data={'perm_statuses': [{'uid': 'system_oneid_all', 'status': 1}]})
        node_perm.refresh_from_db()
        self.assertTrue(node_perm.value)


class UcenterNodeTestCase(TestCase):
    def setUp(self):
        super().setUp()

        owner = User.create_user('owner', 'owner')
        self.owner = self.login_as(owner)
        self._owner = owner
        self.org = Org.create(name='org', owner=owner)

        root = self.org.dept
        level_1 = Dept.valid_objects.create(uid='level_1', name='level_1', parent=root)
        Dept.valid_objects.create(uid='level_2-1', name='level_2-1', parent=level_1, order_no=2)
        Dept.valid_objects.create(uid='level_2-2', name='level_2-2', parent=level_1, order_no=1)
        user = User.create_user('employee', 'employee')
        self._employee = user
        DeptMember.valid_objects.create(user=user, owner=root)
        user = User.create_user('employee_2', 'employee_2')

        root = self.org.group
        role_group = Group.valid_objects.create(uid='role_group_1', name='role_group_1', parent=root, accept_user=False)
        role_1 = Group.valid_objects.create(uid='role_1', name='role_1', parent=role_group, order_no=2)
        Group.valid_objects.create(uid='role_2', name='role_2', parent=role_group, order_no=1)
        GroupMember.valid_objects.create(user=user, owner=role_1)

        self.employee = self.login_as(self._employee)

    def test_node_detail(self):
        root = self.org.dept
        root.visibility = 5    # 均不可见, TODO: 实际这里应因下级可见
        root.save()
        res = self.employee.get(reverse('siteapi:ucenter_node_detail', args=(self.org.dept.node_uid, )))
        self.assertEqual(res.status_code, 404)

        root.visibility = 2    # 直属成员可见
        root.save()
        res = self.employee.get(reverse('siteapi:ucenter_node_detail', args=(self.org.dept.node_uid, )))
        self.assertEqual(res.status_code, 200)
