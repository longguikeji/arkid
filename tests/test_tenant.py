from tests import TestCase

class TestTenantApi(TestCase):

    def test_list_tenants(self):
        '''
        获取租户列表
        '''
        url = '/api/v1/tenants/'
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_tenant(self):
        '''
        获取租户
        '''
        url = '/api/v1/tenants/{}/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_tenant(self):
        '''
        创建租户
        '''
        url = '/api/v1/tenants/'
        body = {
            'name': '创建1',
            'slug': 'slug11',
            'icon': ''
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_update_tenant(self):
        '''
        编辑租户
        '''
        url = '/api/v1/tenants/{}/'.format(self.create_tenant.id)
        body = {
            'name': '创建11',
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_tenant(self):
        '''
        删除租户
        '''
        url = '/api/v1/tenants/{}/'.format(self.create_tenant.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_tenant_config(self):
        '''
        获取租户配置
        '''
        url = '/api/v1/tenants/{}/config/'.format(self.create_tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_tenant_config(self):
        '''
        编辑租户配置
        '''
        url = '/api/v1/tenants/{}/config/'.format(self.create_tenant.id)
        body = {
            'name': '创建1',
            'slug': 'slug11',
            'icon': '',
            'token_duration_minutes': 1440
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_default_tenant(self):
        '''
        获取当前域名下的默认租户(如无slug则为平台租户)
        '''
        url = '/api/v1/default_tenant/'.format(self.create_tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_logout_tenant(self):
        '''
        注销租户
        '''
        url = '/api/v1/tenants/{}/logout/'.format(self.create_tenant.id)
        body = {
            'password': 'admin',
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_tenant_by_slug(self):
        '''
        获取租户slug
        '''
        url = '/api/v1/tenants/tenant_by_slug/{}/'.format(self.create_tenant.slug)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
