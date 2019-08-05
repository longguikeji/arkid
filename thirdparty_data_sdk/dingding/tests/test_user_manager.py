"""
Test Dingding user manager class
"""
# pylint: disable=missing-docstring

import unittest
from unittest import mock
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.user_manager import UserManager
from thirdparty_data_sdk.dingding.dingsdk import constants

TEST_APP_KEY = 'test_app_key'
TEST_APP_SECRET = 'test_app_secret'
TEST_TOKEN = 'test_token'


class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.token_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager')
        self.request_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.request_manager')
        self.mock_token_manager = self.token_patcher.start()
        self.mock_request_manager = self.request_patcher.start()
        self.user_manager = UserManager(
            AccessTokenManager(TEST_APP_KEY, TEST_APP_SECRET))
        self.user_manager.token_manager = self.mock_token_manager
        self.user_manager.request_manager = self.mock_request_manager
        self.user_manager.token = lambda *args, **kwargs: TEST_TOKEN

    def test_get_user_count(self):
        self.mock_request_manager.get.return_value = {
            'count': 6,
            'errcode': 0,
            'errmsg': 'ok'
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.user_manager.get_user_count(True))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.USER_GET_USER_COUNT_URL,
            request_params={
                'access_token': TEST_TOKEN,
                'onlyActive': True
            })

    def test_add_user(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'created',
            'userid': 'zhangsan'
        }
        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.user_manager.add_user('test_add_user', '18210000000', '1'))
        self.mock_request_manager.post.assert_called_with(
            request_url=constants.USER_CREATE_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'name': 'test_add_user',
                'mobile': '18210000000',
                'department': '1',
            })

    def test_update_user(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'updated'
        }
        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.user_manager.update_user(
                't1', mobile='18210000000', department=[1, 2]))
        self.mock_request_manager.post.assert_called_with(
            request_url=constants.USER_UPDATE_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'userid': 't1',
                'mobile': '18210000000',
                'department': [1, 2],
            })

    def test_delete_user(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'deleted'
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.user_manager.delete_user('t1'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.USER_DELETE_URL,
            request_params={
                'access_token': TEST_TOKEN,
                'userid': 't1'
            })

    def test_get_user_detail(self):
        self.mock_request_manager.get.return_value = {
            'errcode':
            0,
            'errmsg':
            'ok',
            'userid':
            'zhangsan',
            'name':
            '张三',
            'tel':
            '010-123333',
            'workPlace':
            '',
            'remark':
            '',
            'mobile':
            '13800000000',
            'email':
            'dingding@aliyun.com',
            'active':
            True,
            'orderInDepts':
            '{1:10, 2:20}',
            'isAdmin':
            False,
            'isBoss':
            False,
            'openId':
            'WsUDaq7DCVIHc6z1GAsYDSA',
            'unionid':
            'cdInjDaq78sHYHc6z1gsz',
            'isLeaderInDepts':
            '{1:true, 2:false}',
            'isHide':
            False,
            'department': [1, 2],
            'position':
            '工程师',
            'avatar':
            'dingtalk.com/abc.jpg',
            'jobnumber':
            '111111',
            'isSenior':
            False,
            'stateCode':
            '86',
            'id':
            394299625,
            'roles': [{
                u'groupName': '岗位',
                'type': 0,
                'id': 394299625,
                'name': '经理'
            }],
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.user_manager.get_user_detail('t1'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.USER_GET_DETAIL_URL,
            request_params={
                'access_token': TEST_TOKEN,
                'userid': 't1'
            })


if __name__ == '__main__':
    unittest.main()
