import logging

from arkid_client.auth.client import AuthClient
from arkid_client.authorizers import NullAuthorizer
from arkid_client.exceptions import ArkIDSDKUsageError


logger = logging.getLogger(__name__)


class ConfidentialAppAuthClient(AuthClient):
    """
    与 ArkID 认证服务端进行通信的 < AuthClient > 类型的认证客户端。
    此客户端必须是已受到 ArkID 官方高度信任的第三方客户端，以至于
    可凭借用户账户名和密码直接向 ArkID 认证端发起授权请求。

    最终，它将得到 ArkID 官方默认的认证参数 `oneid_token` 。
    """

    allowed_authorizer_types = [NullAuthorizer]

    def __init__(self, **kwargs):
        if "authorizer" in kwargs:
            logger.error("参数错误：(`ConfidentialAppClient.authorizer` 非法传入)")
            raise ArkIDSDKUsageError(
                '无法给 < ConfidentialAppAuthClient > 类型客户端装载任何授权器。'
            )

        AuthClient.__init__(
            self,
            authorizer=NullAuthorizer(),
            base_path='login/',
            **kwargs
        )
        self.__certification = None
        self.logger.info("客户端初始化完成")

    def start_auth(self, username: str, password: str):
        """
        开始进行身份认证。

        **Parameters**

            ``username`` (*string*)
              ArkID 官方用户名

            ``password`` (*string*)
              ArkID 官方密码
        """
        self.logger.info("启动 ArkID 官方认证（用户名 + 密码）")
        body = {'username': username, 'password': password}
        self.__certification = self.post(path='', json_body=body)

    def get_token(self):
        """
        获取 oneid_token 。
        """
        return self.__certification.get('token')
