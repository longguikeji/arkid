from tests import TestCase

class TestApproveSystemApi(TestCase):

    def test_list_approve_systems(self):
        '''
        审批系统列表
        '''
        url = '/api/v1/tenant/{}/approve_systems/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_approve_system(self):
        '''
        审批系统获取
        '''
        url = '/api/v1/tenant/{}/approve_systems/{}/'.format(self.tenant.id, self.approve_system.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_approve_system(self):
        '''
        审批系统修改
        '''
        url = '/api/v1/tenant/{}/approve_systems/{}/'.format(self.tenant.id, self.approve_system.id)
        body = {
            "config":{
                "pass_request_url":"",
                "deny_request_url":""
            },
            "name":"一个审批修改",
            "type":"approve_system_arkid",
            "package":"com.longgui.approve.system.arkid"
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_approve_system(self):
        '''
        审批系统删除
        '''
        url = '/api/v1/tenant/{}/approve_systems/{}/'.format(self.tenant.id, self.approve_system.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
