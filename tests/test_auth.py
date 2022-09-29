from tests import TestCase

class TestAuthApi(TestCase):

    def test_auth(self):
        '''
        认证
        '''
        url = '/api/v1/tenant/{}/auth/?event_tag=com.longgui.auth.factor.password.auth'.format(self.tenant.id)
        body = {
            "username":"admin",
            "password":"admin",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_reset_passowrd(self):
        '''
        重置密码
        '''
        url = '/api/v1/tenant/{}/reset_password/?event_tag=com.longgui.auth.factor.password.auth'.format(self.tenant.id)
        body = {
            "username":"admin",
            "password":"admin",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())