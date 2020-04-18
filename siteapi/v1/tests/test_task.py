'''
tests for task api
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse
from django_celery_results.models import TaskResult

from ....siteapi.v1.tests import TestCase


class ImportDingTestCase(TestCase):
    @mock.patch('siteapi.v1.views.task.import_ding')
    def test_run(self, mock_import_ding):
        task = TaskResult.objects.create(task_id='task-id')
        mock_import_ding.delay.return_value = task
        res = self.client.get(reverse('siteapi:import_ding'))
        self.assertEqual(res.status_code, 200)
        expect = {'task_id': 'task-id', 'task_msg': 'import ding'}
        self.assertEqual(res.json(), expect)

        res = self.client.get(reverse('siteapi:task_result', args=('task-id', )))
        expect = {'result': None, 'status': 1, 'status_raw': 'PENDING'}
        self.assertEqual(res.json(), expect)


class InitTestCase(TestCase):
    @mock.patch('siteapi.v1.views.task.init_noah')
    def test_init_noah(self, mock_init_noah):
        mock_init_noah.return_value = True
        res = self.client.get(reverse('siteapi:init_noah'))
        self.assertEqual(res.status_code, 200)
