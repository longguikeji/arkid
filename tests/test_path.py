from tests import TestCase

class TestPathApi(TestCase):

    def test_list_path(self):
        '''
        Openapi path
        '''
        url = '/api/v1/tenant/{}/path_list/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())