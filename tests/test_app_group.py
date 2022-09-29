from tests import TestCase

class TestAppGroupApi(TestCase):

    def test_list_app_groups(self):
        '''
        应用分组列表
        '''
        url = '/api/v1/tenant/{}/app_groups/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_app_group(self):
        '''
        创建应用分组
        '''
        url = '/api/v1/tenant/{}/app_groups/'.format(self.tenant.id)
        body = {
            "name": "新分组"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_app_group(self):
        '''
        获取应用分组
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/'.format(self.tenant.id, self.app_group.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_app_group(self):
        '''
        编辑应用分组
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/'.format(self.tenant.id, self.app_group.id)
        body = {
            "name": "新分组"
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_app_group(self):
        '''
        删除应用分组
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/'.format(self.tenant.id, self.app_group.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_apps_from_group(self):
        '''
        获取当前分组的应用列表
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/apps/'.format(self.tenant.id, self.app_group.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_remove_app_from_group(self):
        '''
        将应用移除出应用分组
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/apps/{}/'.format(self.tenant.id, self.app_group.id, self.app.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_apps_from_group(self):
        '''
        更新当前分组的应用列表
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/apps/'.format(self.tenant.id, self.app_group.id)
        body = {
            "apps": [self.app.id]
        }
        resp = self.client.post(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_exclude_apps(self):
        '''
        获取所有未添加到分组的应用
        '''
        url = '/api/v1/tenant/{}/app_groups/{}/exclude_apps/'.format(self.tenant.id, self.app_group.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())