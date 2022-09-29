from tests import TestCase

class TestAuthRulesApi(TestCase):

    def test_list_auth_rules(self):
        '''
        认证规则列表
        '''
        url = '/api/v1/tenant/{}/auth_rules/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_auth_rule(self):
        '''
        获取认证规则
        '''
        url = '/api/v1/tenant/{}/auth_rules/{}/'.format(self.tenant.id, self.auth_rules.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_auth_rule(self):
        '''
        创建认证规则
        '''
        url = '/api/v1/tenant/{}/auth_rules/'.format(self.tenant.id)
        body = {
            "config":{
                "main_auth_factor":{
                    "id":"70f8d39e30cc40de8a70ec6495c21e84",
                    "name":"default",
                    "package":"com.longgui.auth.factor.password"
                },
                "try_times":3,
                "second_auth_factor":{
                    "id":"7316fc337547450aa4d4038567949ec2",
                    "name":"图形验证码",
                    "package":"com.longgui.auth.factor.authcode"
                },
                "expired":30
            },
            "name":"认证规则:登录失败三次启用图形验证码",
            "type":"retry_times",
            "package":"com.longgui.authrule.retrytimes"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_auth_rule(self):
        '''
        编辑认证规则
        '''
        url = '/api/v1/tenant/{}/auth_rules/{}/'.format(self.tenant.id, self.auth_rules.id)

        body = {
            "config":{
                "main_auth_factor":{
                    "id":"70f8d39e30cc40de8a70ec6495c21e84",
                    "name":"default",
                    "package":"com.longgui.auth.factor.password"
                },
                "try_times":3,
                "second_auth_factor":{
                    "id":"7316fc337547450aa4d4038567949ec2",
                    "name":"图形验证码",
                    "package":"com.longgui.auth.factor.authcode"
                },
                "expired":30
            },
            "name":"认证规则:登录失败三次启用图形验证码",
            "type":"retry_times",
            "package":"com.longgui.authrule.retrytimes"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_auth_rule(self):
        '''
        删除认证规则
        '''
        url = '/api/v1/tenant/{}/auth_rules/{}/'.format(self.tenant.id, self.auth_rules.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
