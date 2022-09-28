from tests import TestCase

class TestApproveActionApi(TestCase):

    def test_list_approve_action(self):
        '''
        审批动作列表
        '''
        url = '/api/v1/tenant/{}/approve_actions/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_approve_action(self):
        '''
        获取审批动作
        '''
        url = '/api/v1/tenant/{}/approve_actions/{}/'.format(self.tenant.id, self.approve_action.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_approve_action(self):
        '''
        创建审批动作
        '''
        url = '/api/v1/tenant/{}/approve_actions/'.format(self.tenant.id)
        body = {
            "name": "测试审批",
            "description": "",
            "path": "/api/v1/tenant/{tenant_id}/apps/{id}/",
            "extension": {
                "name": "默认审批系统",
                "id": str(self.approve_action.extension.id),
            },
            "method": "GET",
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_approve_action(self):
        '''
        编辑审批动作
        '''
        url = '/api/v1/tenant/{}/approve_actions/{}/'.format(self.tenant.id, self.approve_action.id)
        body = {
            "name": "测试审批",
            "description": "",
            "path": "/api/v1/tenant/{tenant_id}/apinfo1/",
            "extension": {
                "name": "默认审批系统",
                "id": str(self.approve_action.extension.id),
            },
            "method": "GET",
        }
        resp = self.client.put(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_approve_action(self):
        '''
        删除审批动作
        '''
        url = '/api/v1/tenant/{}/approve_actions/{}/'.format(self.tenant.id, self.approve_action.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_approve_system_extensions(self):
        '''
        获取审批系统插件列表
        '''
        url = '/api/v1/tenant/{}/approve_system_extensions/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())