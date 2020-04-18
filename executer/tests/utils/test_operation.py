# pylint: disable=missing-docstring
from django.test import TestCase

from ....executer.utils import operation


class OperationTestCase(TestCase):
    def setUp(self):
        pass

    def test_list_diff(self):
        case_1 = {
            'list_a': [1, 2],
            'list_b': [2, 3],
        }
        expect_1 = {
            '>': [1],
            '=': [2],
            '<': [3],
        }
        self.assertEqual(operation.list_diff(**case_1), expect_1)

        case_2 = {
            'list_a': [],
            'list_b': [2, 3],
        }
        expect_2 = {
            '>': [],
            '=': [],
            '<': [2, 3],
        }
        self.assertEqual(operation.list_diff(**case_2), expect_2)
