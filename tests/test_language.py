from tests import TestCase

class TestLanguagesApi(TestCase):

    def test_list_languages(self):
        '''
        获取语言包列表
        '''
        url = '/api/v1/tenant/{}/languages/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_create_language(self):
        '''
        创建自定义语言包
        '''
        url = '/api/v1/tenant/{}/languages/'.format(self.tenant.id)
        body = {
            "name":"新的语言包"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_get_language_data(self):
        '''
        获取自定义语言包
        '''
        url = '/api/v1/tenant/{}/languages/{}/translates/'.format(self.tenant.id, self.language_data.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_translate_word(self):
        '''
        获取自定义语言包
        '''
        url = '/api/v1/tenant/{}/translate_word/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_language(self):
        '''
        删除自定义语言包
        '''
        url = '/api/v1/tenant/{}/languages/{}/'.format(self.tenant.id, self.language_data.id)
        resp = self.client.delete(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())