# pylint: disable=missing-docstring
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ....executer.RDB import RDBExecuter
from ....oneid_meta.models import Group


class RDBGroupExecuterTestCase(TestCase):
    def setUp(self):
        self.root = Group.valid_objects.get(uid='root')
        self.group_1 = Group.valid_objects.create(uid='group_1', parent=self.root)
        self.group_2 = Group.valid_objects.create(uid='group_2', parent=self.group_1)
        self.executer = RDBExecuter()

    def test_move_group_to_group(self):
        with self.assertRaises(ValidationError):
            self.executer.move_group_to_group(self.group_1, self.group_1)
        with self.assertRaises(ValidationError):
            self.executer.move_group_to_group(self.group_1, self.group_2)
        with self.assertRaises(ValidationError):
            self.executer.move_group_to_group(self.root, self.group_2)

        self.executer.move_group_to_group(self.group_2, self.root)
