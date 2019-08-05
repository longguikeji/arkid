# pylint: disable=missing-docstring

from django.test import TestCase

from executer.RDB import RDBExecuter
from executer.tests import GROUP_DATA, PARENT_GROUP_DATA, DEPT_DATA, PARENT_DEPT_DATA
from siteapi.v1.tests.test_user import USER_DATA
from oneid_meta.models import Dept, Group


class BasicTestCase(TestCase):
    maxDiff = None

    def setUp(self):
        self.rdb_executer = RDBExecuter()
        self.root_dept = Dept.valid_objects.get(uid='root')
        self.root_group = Group.valid_objects.get(uid='root')

    def test_user_dn(self):
        user = self.rdb_executer.create_user(USER_DATA)
        self.assertEqual(user.dn, 'uid=employee_1,ou=people,dc=example,dc=org')

    def test_dept_dn(self):
        parent_dept = self.rdb_executer.create_dept(PARENT_DEPT_DATA)
        self.rdb_executer.add_dept_to_dept(parent_dept, self.root_dept)

        dept = self.rdb_executer.create_dept(DEPT_DATA)
        self.assertEqual(dept.dn, 'cn=dev,ou=dept,dc=example,dc=org')
        self.rdb_executer.add_dept_to_dept(dept, parent_dept)

        self.assertEqual(dept.dn, 'cn=dev,cn=IT,ou=dept,dc=example,dc=org')
        self.assertEqual(parent_dept.dn, 'cn=IT,ou=dept,dc=example,dc=org')

        self.assertEqual(self.root_dept.dn, 'ou=dept,dc=example,dc=org')

    def test_group_dn(self):
        parent_group = self.rdb_executer.create_group(PARENT_GROUP_DATA)
        self.rdb_executer.add_group_to_group(parent_group, self.root_group)

        group = self.rdb_executer.create_group(GROUP_DATA)
        self.assertEqual(group.dn, 'cn=supervisor,ou=group,dc=example,dc=org')
        self.rdb_executer.add_group_to_group(group, parent_group)

        self.assertEqual(group.dn, 'cn=supervisor,cn=manager,ou=group,dc=example,dc=org')
        self.assertEqual(parent_group.dn, 'cn=manager,ou=group,dc=example,dc=org')

        self.assertEqual(self.root_group.dn, 'ou=group,dc=example,dc=org')
