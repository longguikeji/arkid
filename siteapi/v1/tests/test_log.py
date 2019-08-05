# pylint: disable=missing-docstring

from django.urls import reverse

from siteapi.v1.tests import TestCase
from siteapi.v1.tests.test_user import USER_DATA
from oneid_meta.models import Log


class LogTestCase(TestCase):
    def setUp(self):
        super().setUp()
        for log in Log.objects.all():
            log.delete()

    def test_get_meta_log(self):
        res = self.client.get(reverse('siteapi:meta_log'))
        self.assertEqual(res.status_code, 200)

    def test_get_log_list(self):
        self.client.json_post(reverse('siteapi:user_list'),
                              data={
                                  'group_uids': ['root'],
                                  'dept_uids': ['root'],
                                  'user': USER_DATA,
                              })
        self.assertEqual(Log.objects.count(), 3)

        url = reverse('siteapi:log_list')
        res = self.client.get(url)

        expect = ['group_member', 'dept_member', 'user_create']
        self.assertEqual(expect, [item['subject'] for item in res.json()['results']])

        res = self.client.get(url, data={'subject': 'ucenter_login'})
        self.assertEqual(res.json()['count'], 0)

        res = self.client.get(url, data={'subject': 'ucenter_login|user_create'})
        self.assertEqual(res.json()['count'], 1)

        res = self.client.get(url, data={'user': 'admi'})
        self.assertEqual(res.json()['count'], 3)
        res = self.client.get(url, data={'user': 'sko'})
        self.assertEqual(res.json()['count'], 0)

        res = self.client.get(url, data={'summary': '用户'})
        self.assertEqual(res.json()['count'], 3)

        res = self.client.get(url, data={'days': 0})
        self.assertEqual(res.json()['count'], 3)

    def test_get_log_detail(self):
        self.client.json_post(reverse('siteapi:user_list'),
                              data={
                                  'group_uids': ['root'],
                                  'dept_uids': ['root'],
                                  'user': USER_DATA,
                              })
        log = Log.objects.first()
        res = self.client.get(reverse('siteapi:log_detail', args=(log.uuid.hex, )))
        self.assertIn('detail', res.json())
