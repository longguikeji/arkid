from tests import TestCase

class TestRegisterApi(TestCase):

    def test_register(self):
        '''
        注册
        '''
        url = '/api/v1/tenant/{}/register/?event_tag=com.longgui.auth.factor.password.register'.format(self.tenant.id)
        body = {
            "username":"dageg1",
            "password":"dageg1",
            "checkpassword":"dageg1",
            "config_id": str(self.register_config.id),
            "privacy":True
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
