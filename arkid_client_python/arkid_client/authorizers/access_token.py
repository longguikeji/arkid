"""
Define AccessTokenAuthorizer
"""
import logging

from arkid_client.authorizers.base import ArkIDAuthorizer
from arkid_client.utils.string_hashing import sha256_string

LOGGER = logging.getLogger(__name__)


class AccessTokenAuthorizer(ArkIDAuthorizer):
    """
    使用 Access Token 进行工作的授权器，其不支持刷新 Tokens。
    将在请求头中设置 Bearer Token 来向 ArkID 服务端发起请求。

    **Parameters**

        ``access_token`` (*str*)
          An access token for ArkID Auth
    """
    def __init__(self, access_token: str):
        LOGGER.info('初始化 < AccessTokenAuthorizer > 类型授权器。' '它将使用 Bearer Token 进行认证操作，' '并且暂不支持处理 401 响应。')
        self.access_token = access_token
        self.header_val = 'Bearer {}'.format(access_token)

        self.access_token_hash = sha256_string(self.access_token)
        LOGGER.debug('Bearer Token 已被加密 ("{}")'.format(self.access_token_hash))

    def set_authorization_header(self, header_dict: dict):
        """
        Sets the `Authorization` header to "Bearer <access_token>"
        """
        LOGGER.debug(('< AccessTokenAuthorizer > 类型授权器设置请求头认证信息，'
                      'Bearer Token 已被加密 ("{}")。').format(self.access_token_hash))
        header_dict["Authorization"] = self.header_val
