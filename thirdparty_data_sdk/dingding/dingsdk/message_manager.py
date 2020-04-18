"""
Dingding message manage api
"""

from ....thirdparty_data_sdk.dingding.dingsdk import constants
from ....thirdparty_data_sdk.dingding.dingsdk.request_manager import RequestManager


class MessageManager():
    """
    Role Manage class, init with AccessTokenManager instance
    """
    def __init__(self, token_manager, agent_id):
        """
        init the MessageManager
        :param AccessTokenManager token_manager: instance of AccessTokenManager
        :param agent_id: Number 企业自建应用是微应用agentId
        """
        self.token_manager = token_manager
        self.request_manager = RequestManager()
        self.agent_id = agent_id

    def asyncsend_text_message(self, text, userid_list=None, dept_id_list=None, to_all_user=None):
        """
        异步发送文本通知，接口返回成功并不表示用户收到通知，需要通过“查询工作通知消息的发送结果”接口查询是否给用户发送成功
        :param text: String 消息内容
        :param userid_list: String 可选
        (userid_list,dept_id_list, to_all_user必须有一个不能为空) 'zhangsan,lisi'
        :param dept_id_list: String 可选 '123,456'
        :param to_all_user: Boolean 可选 是否发送给企业全部用户
        :return: {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }
        """
        if (not userid_list) and (not dept_id_list) and (not to_all_user):
            to_all_user = True

        extra_data = {
            'agent_id': self.agent_id,
            'msg': {
                'msgtype': 'text',
                'text': {
                    'content': text
                }
            },
            'userid_list': userid_list,
            'dept_id_list': dept_id_list,
            'to_all_user': to_all_user
        }

        return self.request_manager.post(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': self.token()},
            request_data=extra_data,
        )

    def asyncsend_image_message(self, media_id, userid_list=None, dept_id_list=None, to_all_user=None):
        """
        异步发送图片通知，接口返回成功并不表示用户收到通知，需要通过“查询工作通知消息的发送结果”接口查询是否给用户发送成功
        :param media_id: String 图片上传得到的media_id
        :param userid_list: String 可选(userid_list,dept_id_list, to_all_user必须有一个不能为空) 'zhangsan,lisi'
        :param dept_id_list: String 可选 '123,456'
        :param to_all_user: Boolean 可选 是否发送给企业全部用户
        :return: {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }
        """
        if (not userid_list) and (not dept_id_list) and (not to_all_user):
            to_all_user = True

        extra_data = {
            'agent_id': self.agent_id,
            'msg': {
                'msgtype': 'image',
                'image': {
                    'media_id': media_id
                }
            },
            'userid_list': userid_list,
            'dept_id_list': dept_id_list,
            'to_all_user': to_all_user
        }

        return self.request_manager.post(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': self.token()},
            request_data=extra_data,
        )

    def asyncsend_file_message(self, media_id, userid_list=None, dept_id_list=None, to_all_user=None):
        """
        异步发送文件通知，接口返回成功并不表示用户收到通知，需要通过“查询工作通知消息的发送结果”接口查询是否给用户发送成功
        :param media_id: String 文件上传得到的media_id
        :param userid_list: String 可选(userid_list,dept_id_list, to_all_user必须有一个不能为空) 'zhangsan,lisi'
        :param dept_id_list: String 可选 '123,456'
        :param to_all_user: Boolean 可选 是否发送给企业全部用户
        :return: {
            'errcode': 0,
            'errmsg': 'ok',
            'task_id': 123
        }
        """
        if (not userid_list) and (not dept_id_list) and (not to_all_user):
            to_all_user = True

        extra_data = {
            'agent_id': self.agent_id,
            'msg': {
                'msgtype': 'file',
                'file': {
                    'media_id': media_id
                }
            },
            'userid_list': userid_list,
            'dept_id_list': dept_id_list,
            'to_all_user': to_all_user
        }

        return self.request_manager.post(
            request_url=constants.MSG_SEND_URL,
            request_params={'access_token': self.token()},
            request_data=extra_data,
        )

    def get_message_send_progress(self, task_id):
        """
        查询工作通知消息的发送进度
        :param task_id:Number 发送消息时钉钉返回的任务id
        :return:{
            'errcode': 0,
            'errmsg': 'ok',
            'progress': {
                'progress_in_percent': 100,
                'status': 2 #(任务执行状态，0=未开始，1=处理中，2=处理完毕)
            }
        }
        """

        extra_data = {'agent_id': self.agent_id, 'task_id': task_id}

        return self.request_manager.post(
            request_url=constants.MSG_GET_SEND_PROGRESS_URL,
            request_params={'access_token': self.token()},
            request_data=extra_data,
        )

    def get_message_send_result(self, task_id):
        """
        查询工作通知消息的发送结果
        :param task_id: Number 异步任务的id
        :return:{
            'send_result': {
            'invalid_user_id_list': 'zhangsan,lisi',
            # 因发送消息过于频繁或超量而被流控过滤后实际未发送的userid。未被限流的接收者仍会被成功发送。
            'forbidden_user_id_list': 'zhangsan,lisi',
            'failed_user_id_list': 'zhangsan,lisi',
            'read_user_id_list': 'zhangsan,lisi',
            'unread_user_id_list': 'zhangsan,lisi',
            'invalid_dept_id_list': '1,2,3'
            },
            'errcode': 0,
            'errmsg': 'ok'
        }
        """

        extra_data = {'agent_id': self.agent_id, 'task_id': task_id}

        return self.request_manager.post(
            request_url=constants.MSG_GET_SEND_RESULT_URL,
            request_params={'access_token': self.token()},
            request_data=extra_data,
        )

    def token(self):
        """
        get_access_token for short
        :return:access_token
        """
        return self.token_manager.get_access_token()
