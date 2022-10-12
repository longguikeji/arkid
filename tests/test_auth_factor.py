from tests import TestCase

class TestAuthFactorApi(TestCase):

    def test_list_auth_factors(self):
        '''
        认证因素列表
        '''
        url = '/api/v1/tenant/{}/auth_factors/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_auth_factor(self):
        '''
        获取认证因素
        '''
        url = '/api/v1/tenant/{}/auth_factors/{}/'.format(self.tenant.id, self.auth_factor.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_auth_factor(self):
        '''
        创建认证因素
        '''
        url = '/api/v1/tenant/{}/auth_factors/'.format(self.tenant.id)
        body = {
            "type":"password",
            "config":{
                "login_enabled":True,
                "register_enabled":True,
                "login_enabled_field_names":[
                    {
                        "key":None
                    }
                ],
                "register_enabled_field_names":[
                    {
                        "key":None
                    }
                ],
                "is_apply":False,
                "regular":"",
                "title":""
            },
            "name":"defaultpass",
            "package":"com.longgui.auth.factor.password"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_auth_factor(self):
        '''
        编辑认证因素
        '''
        url = '/api/v1/tenant/{}/auth_factors/{}/'.format(self.tenant.id, self.auth_factor.id)
        body = {
            "type":"password",
            "config":{
                "login_enabled":True,
                "register_enabled":True,
                "login_enabled_field_names":[
                    {
                        "key":"username"
                    }
                ],
                "register_enabled_field_names":[
                    {
                        "key":"username"
                    }
                ],
                "is_apply":False,
                "regular":"",
                "title":""
            },
            "name":"default",
            "package":"com.longgui.auth.factor.password"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_auth_factor(self):
        '''
        删除认证因素
        '''
        url = '/api/v1/tenant/{}/auth_factors/{}/'.format(self.tenant.id, self.auth_factor.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
