from tests import TestCase

class TestPermissionApi(TestCase):

    def test_create_permission(self):
        '''
        权限创建
        '''
        url = '/api/v1/tenant/{}/permissions'.format(self.tenant.id)
        body = {
            "app": {
                "id": str(self.app.id),
                "name": self.app.name,
            },
            "category": "other",
            "name": "自己创建的权限"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_permissions(self):
        '''
        权限列表
        '''
        url = '/api/v1/tenant/{}/permissions'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_app_permissions(self):
        '''
        应用权限列表
        '''
        url = '/api/v1/tenant/{}/apps/{}/permissions'.format(self.tenant.id, self.app.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_app_last_permissions(self):
        '''
        用户最终结果权限列表
        '''
        url = '/api/v1/tenant/{}/user_app_last_permissions'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_childmanager_permissions(self):
        '''
        子管理员的权限列表
        '''
        url = '/api/v1/tenant/{}/childmanager_permissions'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_permission(self):
        '''
        获取权限
        '''
        url = '/api/v1/tenant/{}/permission/{}'.format(self.tenant.id, self.permission.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_permission(self):
        '''
        修改权限
        '''
        url = '/api/v1/tenant/{}/permission/{}'.format(self.tenant.id, self.permission.id)
        body = {
            "category": "other",
            "name": "自己创建的权限"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_permission(self):
        '''
        删除权限
        '''
        url = '/api/v1/tenant/{}/permission/{}'.format(self.tenant.id, self.permission.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_permission_str(self):
        '''
        权限结果字符串
        '''
        url = '/api/v1/tenant/{}/permissionstr'.format(self.tenant.id, self.permission.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_add_permission(self):
        '''
        添加用户权限
        '''
        url = '/api/v1/tenant/{}/permission/user/{}/add_permission'.format(self.tenant.id, self.user.id)
        body = {
            "data": [str(self.permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_user_add_app_permission(self):
        '''
        添加应用权限
        '''
        url = '/api/v1/tenant/{}/permission/app/{}/add_permission'.format(self.tenant.id, self.app.id)
        body = {
            "data": [str(self.permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
