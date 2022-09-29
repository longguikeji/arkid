from tests import TestCase

class TestDocsApi(TestCase):

    def test_get_docs(self):
        '''
        文档
        '''
        url = '/api/v1/tenant/{}/docs/redoc/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())