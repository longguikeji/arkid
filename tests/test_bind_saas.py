from tests import TestCase

class TestBindSaasApi(TestCase):

    def test_get_bind_saas(self):
        '''
        查询 saas 绑定信息
        '''
        url = '/api/v1/tenant/{}/bind_saas/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_bind_saas_slug(self):
        '''
        查询 saas slug 绑定信息
        '''
        url = '/api/v1/tenant/{}/bind_saas/slug/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_bind_saas_info(self):
        '''
        查询 saas info 绑定信息
        '''
        url = '/api/v1/tenant/{}/bind_saas/info/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
