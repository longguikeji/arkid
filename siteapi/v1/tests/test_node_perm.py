'''
tests for dept perm checker
'''
# pylint: disable=missing-docstring,duplicate-code

from django.urls import reverse
from common.django.drf.client import APIClient

from siteapi.v1.tests import TestCase
from oneid_meta.models import (
    Org,
    Dept,
    User,
    DeptMember,
    Perm,
    UserPerm,
    Group,
    GroupMember,
    ManagerGroup,
    OrgMember,
)


class DeptPermTestCase(TestCase):
    def setUp(self):
        super(DeptPermTestCase, self).setUp()

        owner = User.create_user(username='owner', password='owner')
        self.org = Org.create(name='org', owner=owner)

        root = self.org.dept
        level_1 = Dept.valid_objects.create(uid='l1', name='l1', parent=root)
        Dept.valid_objects.create(uid='l11', name='l11', parent=level_1, order_no=2)
        Dept.valid_objects.create(uid='l12', name='l12', parent=level_1, order_no=1)
        user = User.create_user('employee', 'employee')
        DeptMember.valid_objects.create(user=user, owner=root)
        user = User.create_user('employee_2', 'employee_2')

        token = self.client.post(reverse('siteapi:user_login'), data={
            'username': 'employee',
            'password': 'employee'
        }).json()['token']
        self.employee = APIClient()
        self.employee.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_no_perm(self):
        res = self.anonymous.get(reverse('siteapi:ucenter_node_detail', args=('d_l11', )))
        self.assertEqual(res.status_code, 401)
        res = self.employee.get(reverse('siteapi:ucenter_node_detail', args=('d_l11', )))
        self.assertEqual(res.status_code, 404)
        # GroupMember.valid_objects.create(user=User.valid_objects.get(username='employee'), owner=self.org.direct)
        OrgMember.valid_objects.create(user=User.valid_objects.get(username='employee'), owner=self.org)
        res = self.employee.get(reverse('siteapi:ucenter_node_detail', args=('d_l11', )))
        self.assertEqual(res.status_code, 200)

        res = self.employee.get(reverse('siteapi:dept_tree', args=('l11', )))
        self.assertEqual(res.status_code, 403)
        res = self.employee.get(reverse('siteapi:dept_child_user', args=('l11', )))
        self.assertEqual(res.status_code, 403)
        res = self.employee.get(reverse('siteapi:dept_child_dept', args=('l11', )))
        self.assertEqual(res.status_code, 403)

        res = self.employee.delete(reverse('siteapi:dept_detail', args=('l11', )))
        self.assertEqual(res.status_code, 403)
        res = self.employee.json_post(reverse('siteapi:dept_child_dept', args=('l11', )))
        self.assertEqual(res.status_code, 403)
        res = self.employee.json_patch(reverse('siteapi:dept_child_user', args=('l11', )))
        self.assertEqual(res.status_code, 403)

    def test_node_perm(self):
        perm = Perm.get('dept_nodel1_admin')
        UserPerm.valid_objects.create(owner=User.objects.get(username='employee'), perm=perm, value=True)

        group = Group.objects.create(name='test', parent=self.org.manager)
        ManagerGroup.objects.create(group=group, scope_subject=2, nodes=['d_l11'])
        GroupMember.objects.create(owner=group, user=User.objects.get(username='employee'))
        res = self.employee.json_patch(reverse('siteapi:dept_detail', args=('l11', )), data={'name': 'new'})
        Dept.objects.get(uid='l11')
        self.assertEqual(res.status_code, 200)

        res = self.employee.json_patch(reverse('siteapi:dept_detail', args=('l1', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 403)

    def test_boss(self):
        employee = User.objects.get(username='employee')
        employee.is_boss = True
        employee.save()

        res = self.employee.json_patch(reverse('siteapi:dept_detail', args=('l11', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 200)

        res = self.employee.json_patch(reverse('siteapi:dept_detail', args=('l1', )), data={'name': 'new'})
        self.assertEqual(res.status_code, 200)
