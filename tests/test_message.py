from tests import TestCase

class TestMessageApi(TestCase):

    def test_list_messages(self):
        '''
        消息列表
        '''
        url = '/api/v1/tenant/{}/message/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_message(self):
        '''
        删除消息
        '''
        url = '/api/v1/tenant/{}/message/{}/'.format(self.tenant.id, self.message.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_message(self):
        '''
        创建消息
        '''
        url = '/api/v1/tenant/{}/message/'.format(self.tenant.id)
        body ={
            "user": str(self.user.id),
            "title": "消息标题",
            "content": "消息内容"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())