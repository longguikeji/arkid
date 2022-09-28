from tests import TestCase

class TestAppProtocolApi(TestCase):

    def test_list_app_protocols(self):
        '''
        应用协议列表
        '''
        url = '/api/v1/tenant/{}/app_protocols/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
