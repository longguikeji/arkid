from tests import TestCase

class TestLoginPageApi(TestCase):

    def test_login_page(self):
        '''
        登录与注册
        '''
        url = '/api/v1/tenant/{}/login_page/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())