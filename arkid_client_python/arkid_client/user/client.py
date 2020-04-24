"""
Define UserClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import UserAPIError
from arkid_client.response import ArkIDHTTPResponse


class UserClient(BaseClient):
    """
    用户管理客户端，用于与 ArkID 服务端用户管理相关
    接口的访问操作。
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = UserAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, authorizer=None, **kwargs):
        BaseClient.__init__(self, "user", authorizer=authorizer, **kwargs)

    def query_user(self, **params):
        """
        获取用户信息列表

        :param params:

            ``keyword`` (*str*)
              查询关键字，进行用户名、姓名、邮箱、手机号模糊搜索

            ``wechat_unionid`` (*str*)
              微信客户端 openid

            ``page`` (*int*)
              Default: 1

            ``page_size`` (*int*)
              Default: 30

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 UserClient.query_user_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='', params=params)

    def query_isolated_user(self, **params):
        """
        获取所有独立用户

        :param params:

            ``page`` (*int*)
              Default: 1

            ``page_size`` (*int*)
              Default: 30

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 UserClient.query_isolated_user() 接口与 ArkID 服务端进行交互")
        return self.get(path='isolated/', params=params)

    def query_specified_user(self, username: str):
        """
        获取指定用户的信息

        :param username: 用户唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 UserClient.query_specified_user() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(username))

    def create_user(self, json_body: dict):
        """
        创建用户(需要管理员权限)

        :param json_body:

            ``group_uids`` (*list[*str*]*)
              用户组 uuid 的集合

            ``dept_uids`` (*list[*str*]*)
              部门 uuid 的集合

            ``user`` (*dict*)
              用户的元信息, 参数详情请参考接口文档

            ``node_uids `` (*list[*str*]*)
              （可选的）此字段提供时会忽略 ``group_uids``, ``dept_uids``

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 UserClient.create_user() 接口与 ArkID 服务端进行交互")
        return self.post(path='', json_body=json_body)

    def update_specified_user(self, username: str, json_body: dict):
        """
        修改指定用户的信息

        :param username: 用户唯一标识
        :param json_body: 用户的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 UserClient.update_specified_user() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(username), json_body=json_body)

    def delete_specified_user(self, username: str):
        """
        删除指定用户的信息
        :param username: 用户唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        return self.delete(path='{}/'.format(username))
