"""
Define UserClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import UserAPIError
from arkid_client.response import ArkIDHTTPResponse


class UserClient(BaseClient):
    """
    用户管理客户端，
    用于与 ArkID 服务端用户管理相关接口的访问操作。

    **Methods**

    *  :py:meth:`.query_user`
    *  :py:meth:`.query_isolated_user`
    *  :py:meth:`.query_specified_user`
    *  :py:meth:`.create_user`
    *  :py:meth:`.update_specified_user`
    *  :py:meth:`.delete_specified_user`
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = UserAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "user", authorizer=authorizer, **kwargs)

    def query_user_list(self, **params):
        """
        获取用户信息列表
        (``GET /siteapi/v1/user/``)

        **Parameters**:

            ``keyword`` (*str*)
              查询关键字，进行用户名、姓名、邮箱、手机号模糊搜索

            ``wechat_unionid`` (*str*)
              微信客户端 openid

            ``page`` (*int*)
              用于分页，*Default: 1*

            ``page_size`` (*int*)
              指定分页大小，*Default: 30*

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> users = uc.query_user(...)
        >>> for user in users:
        >>>     print(user['username'], 'id: '
        >>>           ,user['id'])

        **External Documentation**

        关于 `用户的元数据 \
        <https://arkid.docs.apiary.io/#reference/user/0/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 UserClient.query_user_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='', params=params)

    def query_isolated_user(self, **params):
        """
        获取所有独立用户
        (``GET /siteapi/v1/user/isolated/``)

        **Parameters**:

            ``page`` (*int*)
              用于分页，*Default: 1*

            ``page_size`` (*int*)
              指定分页大小，*Default: 30*

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> users = uc.query_isolated_user(...)
        >>> for user in users:
        >>>     print(user['username'], 'id: '
        >>>           ,user['id'])
        """
        self.logger.info("正在调用 UserClient.query_isolated_user() 接口与 ArkID 服务端进行交互")
        return self.get(path='isolated/', params=params)

    def query_user(self, username: str):
        """
        获取指定用户的信息
        (``GET /siteapi/v1/user/<username>/``)

        **Parameters**:

            ``username`` (*str*)
              用户唯一标识

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> user = uc.query_user(...)
        >>> print(user['username'], 'id: '
        >>>       ,user['id'])
        """
        self.logger.info("正在调用 UserClient.query_user() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(username))

    def create_user(self, json_body: dict):
        """
        创建用户(需要管理员权限)
        (``POST /siteapi/v1/user/``)

        **Parameters**:

            ``json_body`` (*dict*)

                ``group_uids`` (*list[str]*)
                  用户组 ``uuid`` 的集合

                ``dept_uids`` (*list[str]*)
                  部门 ``uuid`` 的集合

                ``user`` (*dict*)
                  用户的元信息, 参数详情请参考接口文档

                ``node_uids`` (*list[str]*)
                  （可选的）此字段提供时会忽略 ``group_uids``, ``dept_uids``

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> user_data = {
        >>>   "user": {
        >>>     "password": "example",
        >>>     "username": "example"
        >>>     }
        >>> }
        >>> user = uc.create_user(user_data)
        >>> print(user['username'], 'id: '
        >>>           ,user['id'])

        **External Documentation**

        关于 `用户的元数据 \
        <https://arkid.docs.apiary.io/#reference/user/0/0>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 UserClient.create_user() 接口与 ArkID 服务端进行交互")
        return self.post(path='', json_body=json_body)

    def update_user(self, username: str, json_body: dict):
        """
        修改指定用户的信息
        (``PATCH /siteapi/v1/user/<username>``)

        **Parameters**:

            ``username`` (*str*)
              用户唯一标识

            ``json_body`` (*dict*)
              用户的元信息, 参数详情请参考接口文档

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> query_data = {
        >>>   "password": "example",
        >>>   "private_email": "example@org.com"
        >>> }
        >>> user = uc.update_user(username, query_data)
        >>> print(user['username'], 'id: '
        >>>           ,user['id'])

        **External Documentation**

        关于 `用户的元数据 \
        <https://arkid.docs.apiary.io/#reference/user/2/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 UserClient.update_user() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(username), json_body=json_body)

    def delete_user(self, username: str):
        """
        删除指定用户的信息
        (``DELETE /siteapi/v1/user/<username>``)

        **Parameters**:

            ``username`` (*str*)
              用户唯一标识

        **Examples**

        >>> uc = arkid_client.UserClient(...)
        >>> uc.delete_user(username)
        """
        self.logger.info("正在调用 UserClient.delete_user() 接口与 ArkID 服务端进行交互")
        return self.delete(path='{}/'.format(username))
