from tests import TestCase

class TestPermissionGroupApi(TestCase):

    def test_list_permission_groups(self):
        '''
        权限分组列表
        '''
        url = '/api/v1/tenant/{}/permission_groups/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_permission_group(self):
        '''
        获取权限分组
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/'.format(self.tenant.id, self.system_permission_group.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_create_permission_group(self):
        '''
        创建权限分组
        '''
        url = '/api/v1/tenant/{}/permission_groups/'.format(self.tenant.id)
        body = {
            "app": {
                "id": str(self.app.id),
                "name": self.app.name,
            },
            "name": "新的权限分组"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_permission_group(self):
        '''
        编辑权限分组
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/'.format(self.tenant.id, self.system_permission_group.id)
        body = {
            "name": self.system_permission_group.name
        }
        resp = self.client.put(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_permission_group(self):
        '''
        删除权限分组
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/'.format(self.tenant.id, self.system_permission_group.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_permissions_from_group(self):
        '''
        获取当前分组的权限列表
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/permissions/'.format(self.tenant.id, self.system_permission_group.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_remove_permission_from_group(self):
        '''
        将权限移除出权限分组
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/permissions/{}/'.format(self.tenant.id, self.system_permission_group.id, self.system_permission.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_update_permissions_from_group(self):
        '''
        更新当前分组的权限列表
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/permissions/'.format(self.tenant.id, self.system_permission_group.id)
        body = {
            "data": [str(self.system_permission.id)]
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_get_select_permissions(self):
        '''
        获取所有权限并附加是否在当前分组的状态
        '''
        url = '/api/v1/tenant/{}/permission_groups/{}/select_permissions/'.format(self.tenant.id, self.system_permission_group.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
