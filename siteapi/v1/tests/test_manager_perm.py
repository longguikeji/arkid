'''
tests for manager perm
'''
# pylint: disable=missing-docstring

from siteapi.v1.tests import TestCase
from oneid_meta.models import User, Group, Dept


class ManagerPermTestCase(TestCase):
    '''
    TODO: 复杂数据集供测试
    '''
    def setUp(self):
        super(ManagerPermTestCase, self).setUp()

        employee1 = User.objects.create(username='employee1')
        employee2 = User.objects.create(username='employee2')
        employee3 = User.objects.create(username='employee3')
        employee4 = User.objects.create(username='employee4')

        d_root = Dept.objects.get(uid='root')
        d_dept_1 = Dept.objects.create(parent=d_root, uid='dept_1')
        d_dept_2 = Dept.objects.create(parent=d_root, uid='dept_2')
        d_dept_1_2 = Group.objects.create(parent=d_dept_1)

        g_role = Group.objects.get(uid='role')
        g_role_1 = Group.objects.create(uid='role_1', parent=g_role)
        g_role_2 = Group.objects.create(uid='role_2', parent=g_role)
        g_role_1_2 = Group.objects.create(uid='role_1_2', parent=g_role_1)

        manager_group = Group.objects.get(uid='manager')
        manager_group_1 = Group.objects.create(parent=manager_group, uid='manager_1')
        manager_group_2 = Group.objects.create(parent=manager_group, uid='manager_2')
        manager_group_3 = Group.objects.create(parent=manager_group, uid='manager_3')
