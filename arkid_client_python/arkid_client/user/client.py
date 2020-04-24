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
        BaseClient.__init__(
            self, "user", authorizer=authorizer, **kwargs
        )

    def query_user_list(self, **params):
        self.logger.info("正在调用 UserClient.query_user_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='', params=params)

