from tests import TestCase

class TestWebhookApi(TestCase):

    def test_list_webhooks(self):
        '''
        webhooks列表
        '''
        url = '/api/v1/tenant/{}/webhooks/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_webhook(self):
        '''
        获取webhook
        '''
        url = '/api/v1/tenant/{}/webhooks/{}/'.format(self.tenant.id, self.webhook.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_webhook(self):
        '''
        创建webhook
        '''
        url = '/api/v1/tenant/{}/webhooks/'.format(self.tenant.id)
        body = {
            'name': 'xxx',
            'url': '',
            'secret': 'xxx',
            'events': []
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_webhook(self):
        '''
        修改webhook
        '''
        # url = '/api/v1/tenant/{}/webhooks/{}/'.format(self.tenant.id, self.webhook.id)
        # body = {
        #     'name': 'xxx',
        #     'url': '',
        #     'secret': 'xxx',
        #     'events': [],
        #     'data': {
        #         'name': 'xxx',
        #         'url': '',
        #         'secret': 'xxx',
        #         'events': []
        #     }
        # }
        # resp = self.client.put(url, body ,content_type='application/json')
        # self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_webhook(self):
        '''
        删除webhook
        '''
        url = '/api/v1/tenant/{}/webhooks/{}/'.format(self.tenant.id, self.webhook.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_webhook_histories(self):
        '''
        获取Webhook历史记录列表
        '''
        url = '/api/v1/tenant/{}/webhooks/{}/histories/'.format(self.tenant.id, self.webhook.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_webhook_history(self):
        '''
        获取Webhook历史记录
        '''
        url = '/api/v1/tenant/{}/webhooks/{}/histories/{}/'.format(self.tenant.id, self.webhook.id, self.webhook_triggerhistory.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_webhook_history(self):
        '''
        删除Webhook历史记录
        '''
        url = '/api/v1/tenant/{}/webhooks/{}/histories/{}/'.format(self.tenant.id, self.webhook.id, self.webhook_triggerhistory.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_retry_webhook_history(self):
        '''
        重试webhook历史记录
        '''
        # url = '/api/v1/tenant/{}/webhooks/{}/histories/{}/retry/'.format(self.tenant.id, self.webhook.id, self.webhook_triggerhistory.id)
        # resp = self.client.get(url ,content_type='application/json')
        # self.assertEqual(resp.status_code, 200, resp.content.decode())