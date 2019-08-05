"""
Test Dingding role manager class
"""
# pylint: disable=missing-docstring

import unittest
from unittest import mock
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.role_manager import RoleManager
from thirdparty_data_sdk.dingding.dingsdk import constants

TEST_APP_KEY = 'test_app_key'
TEST_APP_SECRET = 'test_app_secret'
TEST_TOKEN = 'test_token'


class TestRoleManager(unittest.TestCase):
    def setUp(self):
        self.token_patcher = mock.patch('thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager')
        self.request_patcher = mock.patch('thirdparty_data_sdk.dingding.dingsdk.request_manager')
        self.mock_token_manager = self.token_patcher.start()
        self.mock_request_manager = self.request_patcher.start()
        self.role_manager = RoleManager(AccessTokenManager(TEST_APP_KEY, TEST_APP_SECRET))
        self.role_manager.token_manager = self.mock_token_manager
        self.role_manager.request_manager = self.mock_request_manager
        self.role_manager.token = lambda *args, **kwargs: TEST_TOKEN

    def test_get_roles_list(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'result': {
                'hasMore': False,
                'list': [{
                    'name': '默认',
                    'groupId': 1,
                    'roles': [{
                        'name': '管理员',
                        'id': 1
                    }]
                }]
            }
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.get_roles_list(10, 20))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_GET_ROLES_LIST,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'size': 10,
                'offset': 20,
            })

    def test_get_role_userlist(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'result': {
                'hasMore': False,
                'nextCursor': 100,
                'list': [{
                    'userid': 'manager7978',
                    'name': '小钉'
                }]
            }
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.get_role_userlist('5', 10, 20))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_GET_ROLE_USERLIST,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'role_id': '5',
                'size': 10,
                'offset': 20,
            })

    def test_get_role_group(self):
        self.mock_request_manager.get.return_value = {
            'role_group': {
                'roles': [{
                    'role_id': 1,
                    'role_name': '出纳'
                }],
                'group_name': '财务'
            },
            'errcode': 1,
            'errmsg': 'ok'
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.get_role_group(3))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_GET_ROLE_GROUP,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'group_id': 3,
            })

    def test_get_role_detail(self):
        self.mock_request_manager.get.return_value = {
            'role': {
                'name': '财务',
                'groupId': 1002
            },
            'errcode': 0,
            'errmsg': '成功'
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.get_role_detail(3))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_GET_ROLE_DETAIL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'roleId': 3,
            })

    def test_create_role(self):
        self.mock_request_manager.get.return_value = {'roleId': 1, 'errcode': 0, 'errmsg': 'ok'}

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.create_role('test_create', 5))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_CREATE_ROLE,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'roleName': 'test_create',
                'groupId': 5
            })

    def test_update_role(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.update_role('test_update', 7))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_UPDATE_ROL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'roleName': 'test_update',
                'roleId': 7
            })

    def test_delete_role(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
        }

        self.assertEqual(self.mock_request_manager.post.return_value, self.role_manager.delete_role(5))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_DELETE_ROLE,
            request_params={'access_token': TEST_TOKEN},
            request_data={'role_id': 5})

    def test_create_role_group(self):
        self.mock_request_manager.get.return_value = {'groupId': 11, 'errcode': 0, 'errmsg': 'ok'}

        self.assertEqual(self.mock_request_manager.post.return_value,
                         self.role_manager.create_role_group('test_create_group'))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_CREATE_ROLE_GROUP,
            request_params={'access_token': TEST_TOKEN},
            request_data={'name': 'test_create_group'})

    def test_add_users_roles(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': '成功',
        }

        self.assertEqual(self.mock_request_manager.post.return_value,
                         self.role_manager.add_users_roles('1,2,3', 'ab,cd,ef'))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_ADD_USERS_ROLES,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'roleIds': '1,2,3',
                'userIds': 'ab,cd,ef'
            })

    def test_delete_users_roles(self):
        self.mock_request_manager.get.return_value = {'errcode': 0, 'errmsg': '成功'}

        self.assertEqual(self.mock_request_manager.post.return_value,
                         self.role_manager.delete_users_roles('1,2,3', 'ab,cd,ef'))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.ROLE_DEL_USERS_ROLES,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'roleIds': '1,2,3',
                'userIds': 'ab,cd,ef'
            })


if __name__ == '__main__':
    unittest.main()
