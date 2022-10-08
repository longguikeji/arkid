from tests import TestCase

class TestScimSyncApi(TestCase):

    def test_list_scim_syncs(self):
        '''
        用户数据同步配置列表
        '''
        url = '/api/v1/tenant/{}/scim_syncs/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_create_scim_sync(self):
        '''
        创建用户数据同步配置
        '''
        url = '/api/v1/tenant/{}/scim_syncs/'.format(self.tenant.id)
        body = {
            "type":"ArkID",
            "config":{
                "user_url":"",
                "group_url":"",
                "mode":"server"
            },
            "name":"一个新配置",
            "package":"com.longgui.scim.sync.arkid"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_scim_sync(self):
        '''
        获取用户数据同步配置
        '''
        url = '/api/v1/tenant/{}/scim_syncs/{}/'.format(self.tenant.id, self.scim_sync.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_scim_sync(self):
        '''
        编辑用户数据同步配置
        '''
        url = '/api/v1/tenant/{}/scim_syncs/{}/'.format(self.tenant.id, self.scim_sync.id)
        body = {
            "type":"ArkID",
            "config":{
                "user_url":"",
                "group_url":"",
                "mode":"server"
            },
            "name":"一个新配置",
            "package":"com.longgui.scim.sync.arkid"
        }
        resp = self.client.put(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_scim_sync(self):
        '''
        删除用户数据同步配置
        '''
        url = '/api/v1/tenant/{}/scim_syncs/{}/'.format(self.tenant.id, self.scim_sync.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_scim_servers(self):
        '''
        用户数据同步配置列表
        '''
        url = '/api/v1/tenant/{}/scim_server_list/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_start_scim_sync(self):
        '''
        编辑用户数据同步配置
        '''
        url = '/api/v1/tenant/{}/scim_syncs/{}/sync_start/'.format(self.tenant.id, self.scim_sync.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
