"""
Test Dingding department manager class
"""
# pylint: disable=missing-docstring

import unittest
from unittest import mock
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.department_manager import DepartmentManager
from thirdparty_data_sdk.dingding.dingsdk import constants

TEST_APP_KEY = 'test_app_key'
TEST_APP_SECRET = 'test_app_secret'
TEST_TOKEN = 'test_token'


class TestDepartmentManager(unittest.TestCase):
    def setUp(self):
        self.token_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager')
        self.request_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.request_manager')
        self.mock_token_manager = self.token_patcher.start()
        self.mock_request_manager = self.request_patcher.start()
        self.department_manager = DepartmentManager(
            AccessTokenManager(TEST_APP_KEY, TEST_APP_SECRET))
        self.department_manager.token_manager = self.mock_token_manager
        self.department_manager.request_manager = self.mock_request_manager
        self.department_manager.token = lambda *args, **kwargs: TEST_TOKEN

    def test_get_subdep_listids(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'sub_dept_id_list': [2, 3, 4, 5]
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.get_subdep_listids('3'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_GET_SUB_DEP_LIST,
            request_params={
                'access_token': TEST_TOKEN,
                'id': '3'
            })

    def test_list_parent_deps(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'parentIds': [789, 456, 123, 1]
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.list_parent_deps('5'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_LIST_PARENT_DEPS,
            request_params={
                'access_token': TEST_TOKEN,
                'id': '5',
            })

    def test_get_user_list_parentdeps(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'parentIds': [[456, 123, 1], [789, 1]]
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.get_user_list_parentdeps('5'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_USER_LIST_PARENT_DEPS,
            request_params={
                'access_token': TEST_TOKEN,
                'userId': '5',
            })

    def test_get_dep_users(self):
        self.mock_request_manager.get.return_value = {
            'errcode':
            0,
            'errmsg':
            'ok',
            'hasMore':
            False,
            'userlist': [{
                'userid': 'zhangsan',
                'dingId': 'dwdded',
                'mobile': '13122222222',
                'tel': '010-123333',
                'workPlace': '',
                'remark': '',
                'order': 1,
                'isAdmin': True,
                'isBoss': False,
                'isHide': True,
                'isLeader': True,
                'name': '张三',
                'active': True,
                'department': [1, 2],
                'position': '工程师',
                'email': 'zhangsan@alibaba-inc.com',
                'avatar': './dingtalk/abc.jpg',
                'jobnumber': '111111',
                'extattr': {
                    '爱好': '旅游',
                    '年龄': '24'
                }
            }]
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.get_users('1', 0, 30))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_GET_USERS_URL,
            request_params={
                'access_token': TEST_TOKEN,
                'department_id': '1',
                'offset': 0,
                'size': 30,
                'order': 'custom',
            })

    def test_get_dep_users_brief(self):
        self.mock_request_manager.get.return_value = {
            'errcode':
            0,
            'errmsg':
            'ok',
            'hasMore':
            False,
            'userlist': [{
                'userid': 'manager8659',
                'name': '张三'
            }, {
                'userid': 'zhangsan1',
                'name': '张三'
            }],
        }
        self.assertEqual(
            self.mock_request_manager.get.return_value,
            self.department_manager.get_users_brief('5', 2, 20, 'abc'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_USER_SIMPLELIST_URL,
            request_params={
                'access_token': TEST_TOKEN,
                'department_id': '5',
                'offset': 2,
                'size': 20,
                'order': 'abc',
            })

    def test_get_subdep_list(self):
        self.mock_request_manager.get.return_value = {
            'errcode':
            0,
            'errmsg':
            'ok',
            'department': [{
                'id': 2,
                'name': '钉钉事业部',
                'parentid': 1,
                'createDeptGroup': True,
                'autoAddUser': True,
            },
                           {
                               'id': 3,
                               'name': '服务端开发组',
                               'parentid': 2,
                               'createDeptGroup': False,
                               'autoAddUser': False,
                           }]
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.get_subdep_list('5', False))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_GET_DEP_LIST,
            request_params={
                'access_token': TEST_TOKEN,
                'id': '5',
                'fetch_child': False,
            })

    def test_get_dep_detail(self):
        self.mock_request_manager.get.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'id': 2,
            'name': '钉钉事业部',
            'order': 10,
            'parentid': 1,
            'createDeptGroup': True,
            'autoAddUser': True,
            'deptHiding': True,
            'deptPermits': '3|4',
            'userPermits': 'userid1|userid2',
            'outerDept': True,
            'outerPermitDepts': '1|2',
            'outerPermitUsers': 'userid3|userid4',
            'orgDeptOwner': 'manager1122',
            'deptManagerUseridList': 'manager1122|manager3211',
            'sourceIdentifier': 'source'
        }
        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.get_dep_detail('10'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_GET_DETAIL,
            request_params={
                'access_token': TEST_TOKEN,
                'id': '10',
            })

    def test_create_dep(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'created',
            'id': 2
        }

        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.department_manager.create_dep(
                '10', 'test_1', order='1', deptPermits='3|4'))
        self.mock_request_manager.post.assert_called_with(
            request_url=constants.DEPARTMENT_CREATE_DEP,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'order': '1',
                'deptPermits': '3|4',
                'name': 'test_1',
                'parentid': '10',
            })

    def test_update_dep(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'id': 2
        }

        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.department_manager.update_dep(
                '10', name='test_update', order='1', deptPermits='2|5'))
        self.mock_request_manager.post.assert_called_with(
            request_url=constants.DEPARTMENT_UPDATE_DEP,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'order': '1',
                'deptPermits': '2|5',
                'name': 'test_update',
                'id': '10',
            })

    def test_del_dep(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok'
        }

        self.assertEqual(self.mock_request_manager.get.return_value,
                         self.department_manager.delete_dep('10'))
        self.mock_request_manager.get.assert_called_with(
            request_url=constants.DEPARTMENT_DEL_DEP,
            request_params={
                'access_token': TEST_TOKEN,
                'id': '10'
            })


if __name__ == '__main__':
    unittest.main()
