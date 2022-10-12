from tests import TestCase

class TestStatisticsApi(TestCase):

    def test_get_statistics_charts(self):
        '''
        获取统计图表
        '''
        url = '/api/v1/tenant/{}/statistics_charts'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    