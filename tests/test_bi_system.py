from tests import TestCase

class TestBiSystemApi(TestCase):

    def test_list_bi_systems(self):
        '''
        BI系统列表
        '''
        url = '/api/v1/tenant/{}/bi_systems/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
