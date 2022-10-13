from tests import TestCase

class TestUserApi(TestCase):

    def test_list_user(self):
        '''
        用户列表
        '''
        url = '/api/v1/tenant/{}/users/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_user_no_super(self):
        '''
        用户列表，无超级管理员
        '''
        url = '/api/v1/tenant/{}/user_no_super/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_create(self):
        '''
        创建用户
        '''
        url = '/api/v1/tenant/{}/users/'.format(self.tenant.id)
        body = {
            'username': 'shshhs',
            'avatar': ''
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_delete(self):
        '''
        删除用户
        '''
        url = '/api/v1/tenant/{}/users/{}/'.format(self.tenant.id, self.create_user.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_update(self):
        '''
        更新用户
        '''
        url = '/api/v1/tenant/{}/users/{}/'.format(self.tenant.id, self.create_user.id)
        body = {
            'username': 'shshhs',
            'avatar': ''
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_fields(self):
        '''
        用户扩展字段
        '''
        url = '/api/v1/tenant/{}/user_fields/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_user(self):
        '''
        获取用户
        '''
        url = '/api/v1/tenant/{}/users/{}/'.format(self.tenant.id, self.create_user.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
