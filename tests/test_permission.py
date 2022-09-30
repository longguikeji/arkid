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

    def test_user_remove_permission(self):
        '''
        移除用户权限
        '''
        url = '/api/v1/tenant/{}/permission/user/{}/{}/remove_permission'.format(self.tenant.id, self.user.id ,self.permission.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_app_remove_permission(self):
        '''
        移除应用权限
        '''
        url = '/api/v1/tenant/{}/permission/app/{}/{}/remove_permission'.format(self.tenant.id, self.app.id ,self.permission.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_usergroup_add_permission(self):
        '''
        添加用户分组权限
        '''
        url = '/api/v1/tenant/{}/permission/usergroup/{}/add_permission'.format(self.tenant.id, self.system_permission_group.id)
        body = {
            "data": [str(self.permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_usergroup_remove_permission(self):
        '''
        移除用户分组权限
        '''
        url = '/api/v1/tenant/{}/permission/usergroup/{}/{}/remove_permission'.format(self.tenant.id, self.system_permission_group.id, self.permission.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_group_permissions(self):
        '''
        分组权限列表
        '''
        url = '/api/v1/tenant/{}/group_permissions?usergroup_id={}'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_user_group_last_permissions(self):
        '''
        分组权限最终列表
        '''
        url = '/api/v1/tenant/{}/user_group_last_permissions?usergroup_id={}'.format(self.tenant.id, self.user_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_permission_batch_open(self):
        '''
        权限外部访问批量打开
        '''
        url = '/api/v1/tenant/{}/permissions/batch_open'.format(self.tenant.id)
        body = {
            "data": [str(self.permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_permission_batch_close(self):
        '''
        权限外部访问批量关闭
        '''
        url = '/api/v1/tenant/{}/permissions/batch_close'.format(self.tenant.id)
        body = {
            "data": [str(self.permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_permission_toggle_open(self):
        '''
        切换权限是否打开的状态
        '''
        url = '/api/v1/tenant/{}/permission/{}/toggle_open'.format(self.tenant.id, self.permission.id)
        resp = self.client.post(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_permission_toggle_other_user_open(self):
        '''
        切换权限是否开放给本租户其它用户
        '''
        url = '/api/v1/tenant/{}/permission/{}/toggle_other_user_open'.format(self.tenant.id, self.permission.id)
        resp = self.client.post(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
