# pylint: disable=missing-docstring
'''
test for shortcut
'''
from django.urls import reverse

from siteapi.v1.tests import TestCase
from oneid_meta.models import User


class ShortcutTestCase(TestCase):
    def setUp(self):
        super().setUp()
        User.objects.create(username='employee')

    def test_get_slice(self):
        res = self.client.json_post(reverse('siteapi:shortcut_slice'),
                                    data={
                                        'user_uids': ['admin'],
                                        'node_uids': ['d_root'],
                                        'app_uids': ['oneid'],
                                    })
        self.assertEqual(res.json()['users'][0]['username'], 'admin')
        self.assertEqual(res.json()['nodes'][0]['node_uid'], 'd_root')
        self.assertEqual(res.json()['apps'][0]['uid'], 'oneid')

    def test_patch_delete_users(self):
        User.objects.create(username='1')
        User.objects.create(username='2')

        self.client.json_post(reverse('siteapi:shortcut_slice_delete'), data={'user_uids': ['1', '2']})
        self.assertFalse(User.valid_objects.filter(username='1').exists())
        self.assertFalse(User.valid_objects.filter(username='2').exists())
