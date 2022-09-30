from tests import TestCase

'''
权限数据同步配置(缺乏实现)
'''
class TestPermissionSyncApi(TestCase):

    def test_list_permission_syncs(self):
        '''
        权限数据同步配置列表
        '''
        url = '/api/v1/tenant/{}/permission_syncs/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_permission_sync(self):
        '''
        创建权限数据同步配置
        '''
        url = '/api/v1/tenant/{}/permission_syncs/'.format(self.tenant.id)
        resp = self.client.post(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
