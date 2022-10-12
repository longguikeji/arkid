from tests import TestCase

class TestMineApi(TestCase):

    def test_list_mine_apps(self):
        '''
        我的应用列表
        '''
        url = '/api/v1/mine/tenant/{}/apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())
    
    def test_get_mine_profile(self):
        '''
        我的个人资料
        '''
        url = '/api/v1/mine/tenant/{}/profile/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_update_mine_profile(self):
        '''
        更新我的个人资料
        '''
        url = '/api/v1/mine/tenant/{}/profile/'.format(self.tenant.id)
        body = {
            "avatar": "https://img-blog.csdnimg.cn/20211011132942637.png"
        }
        resp = self.client.post(url, body ,content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_permissions(self):
        '''
        我的权限列表
        '''
        url = '/api/v1/mine/tenant/{}/permissions/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_approve_requests(self):
        '''
        我的审批列表
        '''
        url = '/api/v1/mine/tenant/{}/approve_requests/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_switch_tenant(self):
        '''
        租户切换
        '''
        url = '/api/v1/mine/switch_tenant/{}/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_logout(self):
        '''
        退出登录
        '''
        url = '/api/v1/tenant/{}/mine/logout/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_tenants(self):
        '''
        获取我的租户
        '''
        url = '/api/v1/mine/tenants/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_accounts(self):
        '''
        我的绑定账号
        '''
        url = '/api/v1/mine/tenant/{}/accounts/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    # def test_mine_add_permission(self):
    #     '''
    #     添加用户权限
    #     '''
    #     url = '/api/v1/mine/tenant/{}/permissions/{}/add_permisssion'.format(self.tenant.id, self.system_permission.id)
    #     resp = self.client.get(url, content_type='application/json')
    #     self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_unbind_accounts(self):
        '''
        我的没绑定账户
        '''
        url = '/api/v1/mine/tenant/{}/unbind_accounts/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_unbind_mine_account(self):
        '''
        解绑我的账号
        '''
        url = '/api/v1/mine/tenant/{}/accounts/{}/unbind'.format(self.tenant.id, self.github.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_bind_mine_account(self):
        '''
        绑定我的账户
        '''
        url = '/api/v1/mine/tenant/{}/accounts/{}/bind'.format(self.tenant.id, self.github.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_app_groups(self):
        '''
        获取我的应用分组
        '''
        url = '/api/v1/mine/tenant/{}/mine_app_groups/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_apps_with_group(self):
        '''
        获取我的分组应用
        '''
        url = '/api/v1/mine/tenant/{}/mine_group_apps/'.format(self.tenant.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_unread_message(self):
        '''
        我的未读消息列表
        '''
        url = '/api/v1/mine/unread_messages/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_message(self):
        '''
        获取我的消息
        '''
        url = '/api/v1/mine/unread_messages/{}/'.format(self.message.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_message_senders(self):
        '''
        消息发送者
        '''
        url = '/api/v1/mine/message_senders/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_unreaded_message_count(self):
        '''
        未读消息总数
        '''
        url = '/api/v1/mine/unreaded_message_count/'
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())

    def test_get_mine_sender_messages(self):
        '''
        我的消息
        '''
        url = '/api/v1/mine/sender_messages/{}/'.format(self.message.id)
        resp = self.client.get(url, content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.content.decode())