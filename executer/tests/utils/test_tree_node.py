'''
tests for utils.tree_node
'''
# pylint: disable=missing-docstring

from django.test import TestCase

from ....oneid_meta.models import Dept
from ....executer.tests import (DEPT_DATA, PARENT_DEPT_DATA, CHILD_DEPT_1_DATA, CHILD_DEPT_2_DATA)
from ....executer.tests.LDAP.test_executer import LDAPExecuterDeptTestCase
from ....executer.RDB import RDBExecuter
from ....executer.utils import tree_node


class TreeNodeTestCase(TestCase):
    def setUp(self):
        self.root = Dept.valid_objects.get(uid='root')
        self.rdb_executer = RDBExecuter()
        self.dept = self.rdb_executer.create_dept(DEPT_DATA)
        self.parent_dept = self.rdb_executer.create_dept(PARENT_DEPT_DATA)
        self.rdb_executer.add_dept_to_dept(self.parent_dept, self.root)
        self.rdb_executer.add_dept_to_dept(self.dept, self.parent_dept)
        self.child_1_dept = self.rdb_executer.create_dept(CHILD_DEPT_1_DATA)
        self.child_2_dept = self.rdb_executer.create_dept(CHILD_DEPT_2_DATA)
        self.rdb_executer.add_dept_to_dept(self.child_1_dept, self.dept)
        self.rdb_executer.add_dept_to_dept(self.child_2_dept, self.dept)

    def test_get_all_superior_nodes(self):
        res = tree_node.get_all_superior_nodes([self.child_1_dept])
        self.assertEqual(res, set([self.child_1_dept, self.dept, self.parent_dept, self.root]))

        res = tree_node.get_all_superior_nodes([self.child_1_dept, self.child_2_dept])
        self.assertEqual(res, set([self.child_2_dept, self.child_1_dept, self.dept, self.parent_dept, self.root]))

        res = tree_node.get_all_superior_nodes([self.child_1_dept, self.dept])
        self.assertEqual(res, set([self.child_1_dept, self.dept, self.parent_dept, self.root]))

        res = tree_node.get_all_superior_nodes([self.dept, self.parent_dept])
        self.assertEqual(res, set([self.dept, self.parent_dept, self.root]))

        res = tree_node.get_all_superior_nodes([self.parent_dept])
        self.assertEqual(res, set([self.parent_dept, self.root]))

    def test_get_node_path(self):
        self.assertEqual(
            tree_node.get_node_path(self.child_1_dept),
            [self.child_1_dept, self.dept, self.parent_dept, self.root],
        )
        self.assertEqual(
            tree_node.get_node_path(self.parent_dept),
            [self.parent_dept, self.root],
        )

    def test_tree_node_diff(self):
        res = tree_node.tree_node_diff(self.child_1_dept, self.child_2_dept)
        self.assertEqual(res['>'], [self.child_1_dept])
        self.assertEqual(res['<'], [self.child_2_dept])

        res = tree_node.tree_node_diff(self.dept, self.child_2_dept)
        self.assertEqual(res['>'], [])
        self.assertEqual(res['<'], [self.child_2_dept])

    def test_get_dn_path(self):
        dn = 'cn=dev,cn=IT,ou=group,dc=example,dc=org'
        expect = [
            'cn=dev,cn=IT,ou=group,dc=example,dc=org',
            'cn=IT,ou=group,dc=example,dc=org',
            'ou=group,dc=example,dc=org',
            'dc=example,dc=org',
            'dc=org',
        ]
        res = tree_node.get_dn_path(dn)
        self.assertEqual(res, expect)


class DnTreeTestCase(LDAPExecuterDeptTestCase):
    def test_dn_lrd_walker(self):
        res = tree_node.dn_lrd_walker(self.conn, 'ou=dept,dc=example,dc=org')
        expect = [
            'cn=be,cn=dev,cn=IT,ou=dept,dc=example,dc=org',
            'cn=fe,cn=dev,cn=IT,ou=dept,dc=example,dc=org',
            'cn=dev,cn=IT,ou=dept,dc=example,dc=org',
            'cn=tmp,cn=IT,ou=dept,dc=example,dc=org',
            'cn=IT,ou=dept,dc=example,dc=org',
            'ou=dept,dc=example,dc=org',
        ]
        self.assertEqual(list(res), expect)
