from tests import TestCase

class TestAutoAuthApi(TestCase):

    def test_list_auto_auths(self):
        '''
        自动认证列表
        '''
        url = '/api/v1/tenant/{}/auto_auths/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_auto_auth(self):
        '''
        获取自动认证
        '''
        url = '/api/v1/tenant/{}/auto_auths/{}/'.format(self.tenant.id, self.auto_auth.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_auto_auth(self):
        '''
        创建应用
        '''
        url = '/api/v1/tenant/{}/auto_auths/'.format(self.tenant.id)
        body = {
            "config":{
                "service_principal":"http://localhost:8001"
            },
            "name":"test认证",
            "type":"kerberos",
            "package":"com.longgui.auto.auth.kerberos"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_auto_auth(self):
        '''
        编辑自动认证
        '''
        url = '/api/v1/tenant/{}/auto_auths/{}/'.format(self.tenant.id, self.auto_auth.id)
        body = {
            "config":{
                "service_principal":"http://localhost:8001"
            },
            "name":"test认证",
            "type":"kerberos",
            "package":"com.longgui.auto.auth.kerberos"
        }
        resp = self.client.put(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_auto_auth(self):
        '''
        删除自动认证
        '''
        url = '/api/v1/tenant/{}/auto_auths/{}/'.format(self.tenant.id, self.auto_auth.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())