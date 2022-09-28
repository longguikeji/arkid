from tests import TestCase

'''
因为需要和商店交互所有部分接口没写测试
'''
class TestArkstoreApi(TestCase):

    def test_list_arkstore_extensions(self):
        '''
        方舟商店插件列表
        '''
        url = '/api/v1/tenant/{}/arkstore/extensions/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_arkstore_apps(self):
        '''
        方舟商店应用列表
        '''
        url = '/api/v1/tenant/{}/arkstore/apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_arkstore_categorys(self):
        '''
        方舟商店分类列表
        '''
        url = '/api/v1/tenant/{}/arkstore/categorys/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_arkstore_purchased_extensions(self):
        '''
        方舟商店购买插件列表
        '''
        url = '/api/v1/tenant/{}/arkstore/purchased/extensions/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_list_arkstore_purchased_apps(self):
        '''
        方舟商店购买应用列表
        '''
        url = '/api/v1/tenant/{}/arkstore/purchased/apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_rent_arkstore_extension(self):
        '''
        方舟商店租用的插件
        '''
        url = '/api/v1/tenant/{}/arkstore/rent/extensions/{}/'.format(self.tenant.id, 'com.longgui.external.idp.wechatscan')
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())