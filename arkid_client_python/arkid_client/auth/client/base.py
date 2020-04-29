"""
Define AuthClient
"""
import logging

from arkid_client.exceptions import AuthAPIError
from arkid_client.base import BaseClient

LOGGER = logging.getLogger(__name__)


class AuthClient(BaseClient):
    """
    认证客户端，用于向 ArkID 服务端请求授权认证信息，并获取访问令牌。

    **Examples**

    初始化 < AuthClient > 客户端，以 Access Token 授权方式向 ArkID 服务端
    请求对调用的用户进行身份验证 (TODO)

    >>> from arkid_client import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))

    上述使用 oauth2.0 协议来请求授权，虽然 ArkID Client 暂时还不支持这样做。
    但是，这里可以使用任何其它的符合规则的授权器。
    """

    error_class = AuthAPIError

    def __init__(self, base_url, service=None, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, service or "ucenter", authorizer=authorizer, **kwargs)
