from tests import TestCase

class TestExtensionApi(TestCase):

    def test_list_extensions(self):
        '''
        获取平台插件列表
        '''
        url = '/api/v1/extensions/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_get_extension_profile(self):
        '''
        获取插件启动配置
        '''
        url = '/api/v1/extensions/{}/profile/'.format(self.extension.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_extension(self):
        '''
        更新平台插件
        '''
        url = '/api/v1/extensions/{}/'.format(self.extension.id)
        resp = self.client.post(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_extension_markdown(self):
        '''
        获取平台插件的markdown文档
        '''
        url = '/api/v1/extensions/{}/markdown/'.format(self.extension.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_toggle_extension_active_status(self):
        '''
        切换插件启用状态
        '''
        url = '/api/v1/extensions/{}/toggle/'.format(self.extension.id)
        resp = self.client.post(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_toggle_extension_allow_use_platform_config_status(self):
        '''
        切换是否允许租户使用平台配置状态
        '''
        url = '/api/v1/extensions/{}/use_platform_config/toggle/'.format(self.extension.id)
        resp = self.client.post(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())