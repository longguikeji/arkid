from tests import TestCase

class TestThirdAuthApi(TestCase):

    def test_list_third_auths(self):
        '''
        第三方认证列表
        '''
        url = '/api/v1/tenant/{}/third_auths/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_third_auth(self):
        '''
        创建第三方认证
        '''
        url = '/api/v1/tenant/{}/third_auths/'.format(self.tenant.id)
        body = {
            "type":"dingding",
            "config":{
                "app_key":"aa",
                "app_secret":"bb",
                "img_url":"",
                "login_url":"",
                "callback_url":"",
                "bind_url":"",
                "frontend_callback":""
            },
            "name":"sss",
            "package":"com.longgui.external.idp.dingding"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_third_auth(self):
        '''
        编辑第三方认证
        '''
        url = '/api/v1/tenant/{}/third_auths/{}/'.format(self.tenant.id, self.third_auth.id)
        body = {
            "type":"dingding",
            "config":{
                "app_key":"aa",
                "app_secret":"bb",
                "img_url":"",
                "login_url":"",
                "callback_url":"",
                "bind_url":"",
                "frontend_callback":""
            },
            "name":"sss",
            "package":"com.longgui.external.idp.dingding"
        }
        resp = self.client.put(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_third_auth(self):
        '''
        删除第三方认证
        '''
        url = '/api/v1/tenant/{}/third_auths/{}/'.format(self.tenant.id, self.third_auth.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

