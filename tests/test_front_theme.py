from tests import TestCase

class TestFrontThemeApi(TestCase):

    def test_list_front_theme(self):
        '''
        前端主题配置列表
        '''
        url = '/api/v1/tenant/{}/front_theme/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_get_front_theme(self):
        '''
        获取前端主题配置
        '''
        url = '/api/v1/tenant/{}/front_theme/{}/'.format(self.tenant.id, self.front_theme.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_update_front_theme(self):
        '''
        编辑前端主题配置
        '''
        url = '/api/v1/tenant/{}/front_theme/{}/'.format(self.tenant.id, self.front_theme.id)
        body = {
            "type":"materia",
            "config":{
                "priority":1,
                "css_url":"https://bootswatch.com/5/materia/bootstrap.min.css"
            },
            "name":"one test",
            "package":"com.longgui.theme.bootswatch"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_create_front_theme(self):
        '''
        创建前端主题配置
        '''
        url = '/api/v1/tenant/{}/front_theme/'.format(self.tenant.id)
        body = {
            "type":"materia",
            "config":{
                "priority":1,
                "css_url":"https://bootswatch.com/5/materia/bootstrap.min.css"
            },
            "name":"one test",
            "package":"com.longgui.theme.bootswatch"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_front_theme(self):
        '''
        获取前端主题配置
        '''
        url = '/api/v1/tenant/{}/front_theme/{}/'.format(self.tenant.id, self.front_theme.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())