from tests import TestCase

class TestPermissionRuleApi(TestCase):

    def test_list_permission_rules(self):
        '''
        授权规则列表
        '''
        url = '/api/v1/tenant/{}/permission_rules/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_permission_rule(self):
        '''
        获取授权规则
        '''
        url = '/api/v1/tenant/{}/permission_rules/{}/'.format(self.tenant.id, self.permission_rule.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_permission_rule(self):
        '''
        创建授权规则
        '''
        url = '/api/v1/tenant/{}/permission_rules/'.format(self.tenant.id)
        body = {
            "config":{
                "matchfield":{
                    "id":"mobile",
                    "name":"Mobile"
                },
                "matchsymbol":"等于",
                "matchvalue":"15291584673",
                "app":{
                    "id":"arkid",
                    "name":"arkid"
                },
                "permissions":[
                    {
                        "id":"f547ce72-a230-41f6-b3d0-4d68fcc5dff4",
                        "sort_id":9,
                        "name":"公开app列表"
                    }
                ]
            },
            "name":"test",
            "type":"DefaultImpowerRule",
            "package":"com.longgui.impower.rule"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_permission_rule(self):
        '''
        编辑授权规则
        '''
        url = '/api/v1/tenant/{}/permission_rules/{}/'.format(self.tenant.id, self.permission_rule.id)
        body = {
            "config":{
                "matchfield":{
                    "id":"mobile",
                    "name":"Mobile"
                },
                "matchsymbol":"等于",
                "matchvalue":"15291584673",
                "app":{
                    "id":"arkid",
                    "name":"arkid"
                },
                "permissions":[
                    {
                        "id":"f547ce72-a230-41f6-b3d0-4d68fcc5dff4",
                        "sort_id":9,
                        "name":"公开app列表"
                    }
                ]
            },
            "name":"test",
            "type":"DefaultImpowerRule",
            "package":"com.longgui.impower.rule"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_permission_rule(self):
        '''
        删除授权规则
        '''
        url = '/api/v1/tenant/{}/permission_rules/{}/'.format(self.tenant.id, self.permission_rule.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())