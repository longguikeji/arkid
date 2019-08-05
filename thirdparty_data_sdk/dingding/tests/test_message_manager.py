"""
Test Dingding message manager class
"""
# pylint: disable=missing-docstring

import unittest
from unittest import mock
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.message_manager import MessageManager
from thirdparty_data_sdk.dingding.dingsdk import constants

TEST_APP_KEY = 'test_app_key'
TEST_APP_SECRET = 'test_app_secret'
TEST_TOKEN = 'test_token'
TEST_AGENT_ID = 'test_agent_id'


class TestMessageManager(unittest.TestCase):
    def setUp(self):
        self.token_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager')
        self.request_patcher = mock.patch(
            'thirdparty_data_sdk.dingding.dingsdk.request_manager')
        self.mock_token_manager = self.token_patcher.start()
        self.mock_request_manager = self.request_patcher.start()
        self.message_manager = MessageManager(
            AccessTokenManager(TEST_APP_KEY, TEST_APP_SECRET), TEST_AGENT_ID)
        self.message_manager.token_manager = self.mock_token_manager
        self.message_manager.request_manager = self.mock_request_manager
        self.message_manager.token = lambda *args, **kwargs: TEST_TOKEN

    def test_asyncsend_text_message(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }

        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.message_manager.asyncsend_text_message(
                'abc', 'zs,ls', '1,2', False))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'agent_id': TEST_AGENT_ID,
                'msg': {
                    'msgtype': 'text',
                    'text': {
                        'content': 'abc'
                    }
                },
                'userid_list': 'zs,ls',
                'dept_id_list': '1,2',
                'to_all_user': False
            })

    def test_asyncsend_image_message(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }

        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.message_manager.asyncsend_image_message(
                '@image', 'zs,ls', '1,2', False))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'agent_id': TEST_AGENT_ID,
                'msg': {
                    'msgtype': 'image',
                    'image': {
                        'media_id': '@image'
                    }
                },
                'userid_list': 'zs,ls',
                'dept_id_list': '1,2',
                'to_all_user': False
            })

    def test_asyncsend_file_message(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }

        self.assertEqual(
            self.mock_request_manager.post.return_value,
            self.message_manager.asyncsend_file_message(
                '@file', 'zs,ls', '1,2', False))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'agent_id': TEST_AGENT_ID,
                'msg': {
                    'msgtype': 'file',
                    'file': {
                        'media_id': '@file'
                    }
                },
                'userid_list': 'zs,ls',
                'dept_id_list': '1,2',
                'to_all_user': False
            })

    def test_get_message_send_progress(self):
        self.mock_request_manager.post.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'progress': {
                'progress_in_percent': 100,
                'status': 2
            }
        }

        self.assertEqual(self.mock_request_manager.post.return_value,
                         self.message_manager.get_message_send_progress(123))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.MSG_GET_SEND_PROGRESS_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'agent_id': TEST_AGENT_ID,
                'task_id': 123
            })

    def test_get_message_send_result(self):
        self.mock_request_manager.post.return_value = {
            'send_result': {
                'invalid_user_id_list': 'zhangsan,lisi',
                'forbidden_user_id_list': 'zhangsan,lisi',
                'failed_user_id_list': 'zhangsan,lisi',
                'read_user_id_list': 'zhangsan,lisi',
                'unread_user_id_list': 'zhangsan,lisi',
                'invalid_dept_id_list': '1,2,3'
            },
            'errcode': 0,
            'errmsg': 'ok'
        }

        self.assertEqual(self.mock_request_manager.post.return_value,
                         self.message_manager.get_message_send_result(123))

        self.mock_request_manager.post.assert_called_with(
            request_url=constants.MSG_GET_SEND_RESULT_URL,
            request_params={'access_token': TEST_TOKEN},
            request_data={
                'agent_id': TEST_AGENT_ID,
                'task_id': 123
            })


if __name__ == '__main__':
    unittest.main()
