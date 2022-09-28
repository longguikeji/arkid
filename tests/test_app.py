from tests import TestCase

class TestAppApi(TestCase):

    def test_list_apps(self):
        '''
        app列表
        '''
        url = '/api/v1/tenant/{}/apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_open_apps(self):
        '''
        公开app列表
        '''
        url = '/api/v1/tenant/{}/open_apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_all_apps(self):
        '''
        所有app列表
        '''
        url = '/api/v1/tenant/{}/all_apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_all_apps_in_arkid(self):
        '''
        所有app列表(含arkid)
        '''
        url = '/api/v1/tenant/{}/all_apps_in_arkid/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_app(self):
        '''
        获取app
        '''
        url = '/api/v1/tenant/{}/apps/{}/'.format(self.tenant.id, self.app.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_app_read_secret(self):
        '''
        获取应用秘钥
        '''
        url = '/api/v1/tenant/{}/apps/{}/read_secret/'.format(self.tenant.id, self.app.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_app_openapi_version(self):
        '''
        获取app的openapi地址和版本
        '''
        url = '/api/v1/tenant/{}/apps/{}/openapi_version/'.format(self.tenant.id, self.app.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_set_app_openapi_version(self):
        '''
        设置app的openapi地址和版本
        '''
        url = '/api/v1/tenant/{}/apps/{}/openapi_version/'.format(self.tenant.id, self.app.id)
        body = {
            'version': '1',
            'openapi_uris': 'http://127.0.0.1:8000/api/v1/openapi.json',
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_app(self):
        '''
        修改app
        '''
        url = '/api/v1/tenant/{}/apps/{}/'.format(self.tenant.id, self.app.id)
        body = {
            'name': '预置应用',
            'url': '',
            'logo': '',
            'description': '',
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_set_app_config(self):
        '''
        配置应用协议
        '''
        url = '/api/v1/tenant/{}/apps/{}/config/'.format(self.tenant.id, self.app.id)
        body = {
            "app_type":"OIDC",
            "config":{
                "skip_authorization":True,
                "redirect_uris":"https://www.baidu.com",
                "client_type":"confidential",
                "grant_type":"authorization-code",
                "algorithm":"RS256",
                "client_id":"",
                "client_secret":"",
                "authorize":"",
                "token":"",
                "userinfo":"",
                "logout":"",
                "issuer_url":""
            },
            "package":"com.longgui.app.protocol.oidc"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_app_config(self):
        '''
        获取应用协议数据
        '''
        url = '/api/v1/tenant/{}/apps/{}/config/'.format(self.tenant.id, self.app.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_sync_app_permission(self):
        '''
        同步应用权限
        '''
        url = '/api/v1/apps/{}/sync_permission/'.format(self.app.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_app(self):
        '''
        创建应用
        '''
        url = '/api/v1/tenant/{}/apps/'.format(self.tenant.id)
        body = {
            'name': '预置应用1',
            'url': '',
            'logo': '',
            'description': '',
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_app(self):
        '''
        删除app
        '''
        url = '/api/v1/tenant/{}/apps/{}/'.format(self.tenant.id, self.app.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())