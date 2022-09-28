from tests import TestCase

class TestAccountLifeApi(TestCase):

    def test_list_account_lifes(self):
        '''
        账号生命周期配置列表
        '''
        url = '/api/v1/tenant/{}/account_lifes/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_account_life(self):
        '''
        获取账号生命周期配置
        '''
        url = '/api/v1/tenant/{}/account_lifes/{}/'.format(self.tenant.id, self.account_life.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_create_account_life(self):
        '''
        创建账号生命周期配置
        '''
        url = '/api/v1/tenant/{}/account_lifes/'.format(self.tenant.id)
        body = {
            "config":[
                {
                    "user":{
                        "id":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
                        "username":"admin"
                    },
                    "expiration_time":"2023-09-28 15:34:00"
                }
            ],
            "name":"生命周期1",
            "type":"user_expiration",
            "package":"com.longgui.account.life.arkid"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_account_life(self):
        '''
        编辑账号生命周期配置
        '''
        url = '/api/v1/tenant/{}/account_lifes/{}/'.format(self.tenant.id, self.account_life.id)
        body = {
            "config":[
                {
                    "user":{
                        "id":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
                        "username":"admin"
                    },
                    "expiration_time":"2023-09-28 15:34:00"
                }
            ],
            "name":"生命周期1",
            "type":"user_expiration",
            "package":"com.longgui.account.life.arkid"
        }
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_account_life(self):
        '''
        删除账号生命周期配置
        '''
        url = '/api/v1/tenant/{}/account_lifes/{}/'.format(self.tenant.id, self.account_life.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_account_life_crontab(self):
        '''
        获取账号生命周期定时任务配置
        '''
        url = '/api/v1/tenant/{}/account_life_crontab/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_account_life_crontab(self):
        '''
        更新账号生命周期定时任务配置
        '''
        url = '/api/v1/tenant/{}/account_life_crontab/'.format(self.tenant.id)
        body = {"crontab":"10","max_retries":10,"retry_delay":10}
        resp = self.client.put(url, body, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())