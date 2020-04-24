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
    请求对调用的用户进行身份验证。
    >>> from arkid_client import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))

    当然，这里可以使用任何其它的符合规则的授权器。

    **Methods**

    *  :py:meth:`.oidc_get_authorize_url`
    *  :py:meth:`.oidc_exchange_code_for_tokens`
    *  :py:meth:`.AuthClient.oidc_refresh_token`
    *  :py:meth:`.oidc_validate_token`
    *  :py:meth:`.oidc_revoke_token`
    *  :py:meth:`.oidc_token`
    *  :py:meth:`.oidc_userinfo`

    """

    error_class = AuthAPIError

    def __init__(self, service=None, authorizer=None, **kwargs):
        BaseClient.__init__(self, service or "ucenter", authorizer=authorizer, **kwargs)
