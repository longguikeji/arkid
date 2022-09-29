from tests import TestCase

import json

class TestChildManagerApi(TestCase):

    def test_list_child_managers(self):
        '''
        子管理员列表
        '''
        url = '/api/v1/tenant/{}/child_managers/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_child_manager(self):
        '''
        获取子管理员
        '''
        url = '/api/v1/tenant/{}/child_managers/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        result = json.loads(resp.content.decode())
        items = result.get('items', [])
        for item in items:
            user_id = item.get('id')
            # 取一个子管理员
            url = '/api/v1/tenant/{}/child_managers/{}/'.format(self.tenant.id, user_id)
            resp = self.client.get(url, content_type='application/json')
            self.assertEqual(resp.status_code, 200, resp.content.decode())
            break

    def test_update_child_manager(self):
        '''
        编辑子管理员
        '''
        url = '/api/v1/tenant/{}/child_managers/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        result = json.loads(resp.content.decode())
        items = result.get('items', [])
        for item in items:
            user_id = item.get('id')
            # 取一个子管理员
            url = '/api/v1/tenant/{}/child_managers/{}/'.format(self.tenant.id, user_id)
            body = {
                "permissions":[
                ],
                "manager_scope":[
                ]
            }
            resp = self.client.post(url,body,content_type='application/json')
            self.assertEqual(resp.status_code, 200, resp.content.decode())
            break

    def test_delete_child_manager(self):
        '''
        删除子管理员
        '''
        url = '/api/v1/tenant/{}/child_managers/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        result = json.loads(resp.content.decode())
        items = result.get('items', [])
        for item in items:
            user_id = item.get('id')
            # 取一个子管理员
            url = '/api/v1/tenant/{}/child_managers/{}/'.format(self.tenant.id, user_id)
            resp = self.client.delete(url,content_type='application/json')
            self.assertEqual(resp.status_code, 200, resp.content.decode())
            break

    def test_create_child_manager(self):
        '''
        创建子管理员
        '''
        url = '/api/v1/tenant/{}/child_managers/'.format(self.tenant.id)
        body = {
            "users":[
            ],
            "permissions":[
            ],
            "manager_scope":[
            ]
        }
        resp = self.client.post(url,body,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())