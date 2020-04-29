"""
Define NullAuthorizer
"""
import logging

from arkid_client.authorizers.base import ArkIDAuthorizer

LOGGER = logging.getLogger(__name__)


class NullAuthorizer(ArkIDAuthorizer):
    """
    该授权器不实现任何身份验证功能，并尝试去掉请求头部的认证信息。
    """
    def set_authorization_header(self, header_dict):
        """
        如果存在授权头部信息，则从给定头部信息的 ``dict`` 中尝试删除授权标头。
        """
        LOGGER.debug("< NullAuthorizer >: 确保请求头部不存在认证信息。")
        header_dict.pop("Authorization", None)
