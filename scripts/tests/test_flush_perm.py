'''
tests for flush perm
'''

# pylint: disable=missing-docstring
from django.test import TestCase

from oneid_meta.models import Dept, DeptPerm, Perm, User
from executer.RDB import RDBExecuter
from scripts.flush_perm import flush_dept_perm, flush_user_perm


class TreeFlushPermTestCase(TestCase):
    def setUp(self):
        self.rdb_executer = RDBExecuter()

        self.user = User.create_user('user', 'user')

        self.root = Dept.valid_objects.get(uid='root')
        self.dept_1 = Dept.valid_objects.create(uid='1', parent=self.root)
        self.dept_1_1 = Dept.valid_objects.create(
            uid='1_1', parent=self.dept_1)
        self.dept_1_2 = Dept.valid_objects.create(
            uid='1_2', parent=self.dept_1)
        self.dept_1_1_1 = Dept.valid_objects.create(
            uid='1_1_1', parent=self.dept_1_1)
        self.dept_1_1_2 = Dept.valid_objects.create(
            uid='1_1_2', parent=self.dept_1_1)
        self.dept_1_1_3 = Dept.valid_objects.create(
            uid='1_1_3', parent=self.dept_1_1)
        self.dept_2 = Dept.valid_objects.create(uid='2', parent=self.root)
        self.dept_2_1 = Dept.valid_objects.create(
            uid='2_1', parent=self.dept_2)
        self.dept_2_2 = Dept.valid_objects.create(
            uid='2_2', parent=self.dept_2)

        self.front_walker_depts = [
            self.root,
            self.dept_1,
            self.dept_1_1,
            self.dept_1_1_1,
            self.dept_1_1_2,
            self.dept_1_1_3,
            self.dept_1_2,
            self.dept_2,
            self.dept_2_1,
            self.dept_2_2,
        ]

        self.perm = Perm.valid_objects.create(uid='perm')
        for dept in self.front_walker_depts:
            DeptPerm.valid_objects.create(owner=dept, perm=self.perm)

    def test_tree_front_walker(self):
        self.assertEqual(
            list(self.root.tree_front_walker()), self.front_walker_depts)

    def test_dept_status(self):
        DeptPerm.valid_objects.get(
            owner=self.root, perm=self.perm).update_status(1)
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        expect = [
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
        ]
        self.assertEqual(res, expect)

        DeptPerm.valid_objects.get(
            owner=self.root, perm=self.perm).update_status(0)
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        expect = [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.assertEqual(res, expect)

        DeptPerm.valid_objects.get(
            owner=self.dept_1, perm=self.perm).update_status(1)
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        expect = [
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
        ]
        self.assertEqual(res, expect)

        DeptPerm.valid_objects.get(
            owner=self.dept_1_1, perm=self.perm).update_status(0)
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        expect = [
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
        ]
        self.assertEqual(res, expect)

    def test_flush_dept_perm(self):
        dept_perm = self.dept_1_1.get_perm(self.perm)
        dept_perm.status = 1
        dept_perm.save()

        previous = [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        self.assertEqual(previous, res)

        flush_dept_perm()

        expect = [
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
        ]
        res = [
            DeptPerm.valid_objects.get(owner=dept, perm=self.perm).value
            for dept in self.front_walker_depts
        ]
        self.assertEqual(DeptPerm.valid_objects.filter(value=True).count(), 4)
        self.assertEqual(expect, res)

    def test_flush_user_perm(self):
        self.rdb_executer.add_user_to_depts(self.user, [self.dept_1_2])
        dept_perm = self.dept_1_1.get_perm(self.perm)
        dept_perm.status = 1
        dept_perm.save()
        flush_dept_perm()

        flush_user_perm()
        self.assertFalse(self.user.get_perm(self.perm).value)
        self.assertFalse(self.user.get_perm(self.perm).dept_perm_value)

        self.rdb_executer.add_user_to_depts(self.user, [self.dept_1_1])
        flush_user_perm()
        self.assertTrue(self.user.get_perm(self.perm).value)
        self.assertTrue(self.user.get_perm(self.perm).dept_perm_value)
