from tests import TestCase

class TestPlatfromApi(TestCase):

    def test_get_platform_config(self):
        '''
        获取平台配置
        '''
        url = '/api/v1/platform_config/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_platform_config_with_no_permission(self):
        '''
        获取平台配置
        '''
        url = '/api/v1/platform_config_with_no_permission/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_platform_config(self):
        '''
        更新平台配置
        '''
        url = '/api/v1/platform_config/'
        body = {
            "is_saas": False,
            "is_need_rent": False
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_frontend_url(self):
        '''
        获取ArkId访问地址
        '''
        url = '/api/v1/frontend_url/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_set_frontend_url(self):
        '''
        设置ArkId访问地址
        '''
        url = '/api/v1/frontend_url/'
        body = {
            "url": "http://www.db.com"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_version(self):
        '''
        获取ArkId版本
        '''
        url = '/api/v1/version/'
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())