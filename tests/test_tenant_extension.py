from tests import TestCase

class TestTenantExtensionApi(TestCase):

    def test_create_extension_config(self):
        '''
        租户下，创建插件运行时配置
        '''
        url = '/api/v1/tenant/{}/extension/{}/config/'.format(self.tenant.id, self.extension.id)
        body = {
            "package":"com.longgui.external.idp.feishu",
            "name":"feishu",
            "config":{
                "app_id":"cli_a26d2ee3b2fad013",
                "app_secret":"gnX0MgFhsXQUa0aamUYrgcNb15HBzz1T",
                "img_url":"https://p6-hera.byteimg.com/tos-cn-i-jbbdkfciu3/f3de430ed2b64f90a95fb8a393dfa6bd~tplv-jbbdkfciu3-image:0:0.image",
                "login_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/login",
                "callback_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/callback",
                "bind_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/bind"
            }
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_extension_config(self):
        '''
        租户下，插件运行时配置列表
        '''
        url = '/api/v1/tenant/{}/extension/{}/config/{}/'.format(self.tenant.id, self.scim_sync.extension.id, self.scim_sync.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_extension_config(self):
        '''
        租户下，插件运行时配置列表
        '''
        if self.feishu:
            url = '/api/v1/tenant/{}/extension/{}/config/{}/'.format(self.tenant.id, self.feishu.extension.id, self.feishu.id)
            body = {
                "package":"com.longgui.external.idp.feishu",
                "name":"feishu",
                "config":{
                    "app_id":"cli_a26d2ee3b2fad013",
                    "app_secret":"gnX0MgFhsXQUa0aamUYrgcNb15HBzz1T",
                    "img_url":"https://p6-hera.byteimg.com/tos-cn-i-jbbdkfciu3/f3de430ed2b64f90a95fb8a393dfa6bd~tplv-jbbdkfciu3-image:0:0.image",
                    "login_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/login",
                    "callback_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/callback",
                    "bind_url":"http://localhost:9528/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/bind"
                }
            }
            resp = self.client.post(url, body ,content_type='application/json')
            self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_extension_config(self):
        '''
        租户下，插件运行时配置列表
        '''
        url = '/api/v1/tenant/{}/extension/{}/config/'.format(self.tenant.id, self.scim_sync.extension.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_delete_extension_config(self):
        '''
        租户下，删除插件运行时配置
        '''
        url = '/api/v1/tenant/{}/extension/{}/config/{}/'.format(self.tenant.id, self.scim_sync.extension.id, self.scim_sync.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_create_extension_settings(self):
        '''
        租户下，创建插件配置
        '''
        url = '/api/v1/tenant/{}/extension/{}/settings/'.format(self.tenant.id, self.scim_sync.extension.id, self.scim_sync.id)
        body = {
            "package":"com.longgui.external.idp.feishu",
            "is_active":False,
            "use_platform_config":False
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_extension_settings(self):
        '''
        租户下，获取插件配置
        '''
        url = '/api/v1/tenant/{}/extension/{}/settings/'.format(self.tenant.id, self.scim_sync.extension.id, self.scim_sync.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_platform_extensions(self):
        '''
        平台插件列表
        '''
        url = '/api/v1/tenant/{}/platform/extensions/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_tenant_extensions(self):
        '''
        租户插件列表
        '''
        url = '/api/v1/tenant/{}/tenant/extensions/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_toggle_tenant_extension_status(self):
        '''
        切换插件状态
        '''
        if self.feishu:
            url = '/api/v1/tenant/{}/tenant/extensions/{}/active/'.format(self.tenant.id, self.feishu.extension.id)
            resp = self.client.post(url ,content_type='application/json')
            self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_extension(self):
        '''
        获取租户插件
        '''
        url = '/api/v1/tenant/{}/tenant/extensions/{}/'.format(self.tenant.id, self.extension.id)
        resp = self.client.post(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_extension(self):
        '''
        删除租户插件
        '''
        url = '/api/v1/tenant/{}/extensions/{}/'.format(self.tenant.id, self.extension.id)
        resp = self.client.delete(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_config_select(self):
        '''
        分类获取租户下插件配置列表
        '''
        url = '/api/v1/tenants/{}/config_select/'.format(self.tenant.id)
        resp = self.client.get(url ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())