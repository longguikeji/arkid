from tests import TestCase

class TestEventApi(TestCase):

    def test_list_events(self):
        '''
        事件列表
        '''
        url = '/api/v1/tenant/{}/event_list/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())