"""
Define BasicAuthorizer
"""
import logging

from arkid_client.authorizers.base import ArkIDAuthorizer
from arkid_client.utils.string_hashing import sha256_string

LOGGER = logging.getLogger(__name__)


class BasicAuthorizer(ArkIDAuthorizer):
    """
    使用 ArkID 官方默认的 oneid_token 进行基本认证。
    将在请求头中设置 Token 来向 ArkID 服务端发起请求。
    **Parameters**

        ``oneid_token`` (*str*)
          An basic token for ArkID Auth
    """
    def __init__(self, oneid_token: str):
        LOGGER.info('正在初始化{}类型授权器。' '它将使用 oneid_token 进行认证操作，' '并且暂不支持处理 401 响应。'.format(type(self)))
        self.oneid_token = oneid_token
        self.header_val = 'token {}'.format(oneid_token)
        self.oneid_token_hash = sha256_string(self.oneid_token)
        LOGGER.debug('Oneid Token 已被加密 ("{}")'.format(self.oneid_token_hash))

    def set_authorization_header(self, header_dict: dict):
        """
        Sets the `Authorization` header to "token <oneid_token>"
        """
        LOGGER.debug('正在设置认证信息，' 'Oneid Token 已被授权器加密 ("{}")。'.format(self.oneid_token_hash))
        header_dict["Authorization"] = self.header_val
