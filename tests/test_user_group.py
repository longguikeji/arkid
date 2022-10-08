from tests import TestCase

class TestUserGroupApi(TestCase):

    def test_create_group(self):
        '''
        分组创建
        '''
        url = '/api/v1/tenant/{}/user_groups/'.format(self.tenant.id)
        body = {
            'name': 'fenzu111'
        }
        resp = self.client.get(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_list_groups(self):
        '''
        分组列表
        '''
        url = '/api/v1/tenant/{}/user_groups/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_group(self):
        '''
        获取分组
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_group(self):
        '''
        修改分组
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/'.format(self.tenant.id, self.user_group.id)
        body = {
            'name': 'xxxa'
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_group(self):
        '''
        删除分组
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/'.format(self.tenant.id, self.user_group.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_group_users(self):
        '''
        获取分组用户
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/users/'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_group_users_add(self):
        '''
        分组添加用户
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/users/'.format(self.tenant.id, self.user_group.id)
        body = {
            'user_ids': [self.user.id]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_group_batch_users_remove(self):
        '''
        分组批量移除用户
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/batch_users/'.format(self.tenant.id, self.user_group.id)
        body = {
            'user_ids': [self.user.id]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_group_users_remove(self):
        '''
        分组移除用户
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/users/{}/'.format(self.tenant.id, self.user_group.id, self.user.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_exclude_users(self):
        '''
        获取所有未添加到分组的用户
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/exclude_users/'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_user_group_all_permissions(self):
        '''
        获取所有权限并附带是否已授权给用户分组状态
        '''
        url = '/api/v1/tenant/{}/user_groups/{}/all_permissions/'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())