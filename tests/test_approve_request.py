from tests import TestCase

class TestApproveRequestApi(TestCase):

    def test_list_approve_requests(self):
        '''
        审批请求
        '''
        url = '/api/v1/tenant/{}/approve_requests/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())