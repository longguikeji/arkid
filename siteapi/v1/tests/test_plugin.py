# pylint: disable=missing-docstring

from django.urls import reverse

from siteapi.v1.tests import TestCase


class CrontabPluginTestCase(TestCase):
    def test_crontab_plugin_list(self):
        res = self.client.get(reverse('siteapi:crontab_plugin_list'))
        expect = [{
            'is_active': False,
            'import_path': 'plugins.crontab.demo.maintain_admin_name_plugin',
            'schedule': ''
        }]
        self.assertEqual(expect, [self.extract(item, ['is_active', 'import_path', 'schedule']) for item in res.json()])

    def test_crontab_plugin_detail(self):
        uuid = self.client.get(reverse('siteapi:crontab_plugin_list')).json()[0]['uuid']
        url = reverse('siteapi:crontab_plugin_detail', args=(uuid, ))
        res = self.client.get(url)
        expect = {'is_active': False, 'import_path': 'plugins.crontab.demo.maintain_admin_name_plugin', 'schedule': ''}
        self.assertEqualScoped(expect, res.json(), keys=['is_active', 'import_path', 'schedule'])

        res = self.client.json_patch(url, data={
            'is_active': True,
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'schedule': ['this field is required']})

        res = self.client.json_patch(url, data={
            'is_active': True,
            'schedule': '* * * bad *',
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.json_patch(url, data={
            'is_active': True,
            'schedule': '* * * * *',
        })
        self.assertEqual(res.status_code, 200)

        res = self.client.json_patch(url, data={
            'is_active': True,
            'schedule': '*/5 * * * *',
        })
        self.assertEqual(res.status_code, 200)


class MiddlewarePluginTestCase(TestCase):
    def test_middleware_plugin_list(self):
        res = self.client.get(reverse('siteapi:middleware_plugin_list'))
        expect = [{'is_active': False, 'import_path': 'plugins.middleware.demo.localhostonly_plugin', 'order_no': 0}]
        self.assertEqual(expect, [self.extract(item, ['is_active', 'import_path', 'order_no']) for item in res.json()])

    def test_middleware_plugin_detail(self):
        uuid = self.client.get(reverse('siteapi:middleware_plugin_list')).json()[0]['uuid']
        url = reverse('siteapi:middleware_plugin_detail', args=(uuid, ))
        res = self.client.get(url)
        expect = {'is_active': False, 'import_path': 'plugins.middleware.demo.localhostonly_plugin', 'order_no': 0}
        self.assertEqualScoped(expect, res.json(), keys=['is_active', 'import_path', 'order_no'])

        res = self.client.json_patch(url, data={
            'is_active': True,
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['is_active'])
