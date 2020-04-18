# pylint: disable=missing-docstring
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ....executer.RDB import RDBExecuter
from ....oneid_meta.models import Dept


class RDBDeptExecuterTestCase(TestCase):
    def setUp(self):
        self.root = Dept.valid_objects.get(uid='root')
        self.dept_1 = Dept.valid_objects.create(uid='dept_1', parent=self.root)
        self.dept_2 = Dept.valid_objects.create(uid='dept_2', parent=self.dept_1)
        self.executer = RDBExecuter()

    def test_move_dept_to_dept(self):
        with self.assertRaises(ValidationError):
            self.executer.move_dept_to_dept(self.dept_1, self.dept_1)
        with self.assertRaises(ValidationError):
            self.executer.move_dept_to_dept(self.dept_1, self.dept_2)
        with self.assertRaises(ValidationError):
            self.executer.move_dept_to_dept(self.root, self.dept_2)

        self.executer.move_dept_to_dept(self.dept_2, self.root)
