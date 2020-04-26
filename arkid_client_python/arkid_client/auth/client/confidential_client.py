"""
Define ConfidentialAppAuthClient
"""
from arkid_client.auth.client import AuthClient
from arkid_client.authorizers import NullAuthorizer
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.exceptions import ArkIDSDKUsageError
from arkid_client.base import reload_service, reload_authorizer


class ConfidentialAppAuthClient(AuthClient):
    """
    与 ArkID 认证服务端进行通信的 < AuthClient > 类型的认证客户端。
    此客户端必须是已受到 ArkID 官方高度信任的第三方客户端，可凭借用
    户账户名和密码直接向 ArkID 认证端发起授权请求。
    最终，它将得到 ArkID 官方默认的认证凭证 `oneid_token` 。
    """

    allowed_authorizer_types = [
        NullAuthorizer,
        BasicAuthorizer,
    ]

    def __init__(self, base_url, **kwargs):
        if "authorizer" in kwargs:
            self.logger.error("参数错误：(`ConfidentialAppClient.authorizer` 非法传入)")
            raise ArkIDSDKUsageError('无法给 < ConfidentialAppAuthClient > 类型客户端装载任何授权器。')

        AuthClient.__init__(self, authorizer=NullAuthorizer(), base_url=base_url, **kwargs)
        self.__certification = None
        self.logger.info("客户端初始化完成")

    def start_auth(self, username: str, password: str):
        """
        开始进行身份认证
        :param username: 用户唯一标识
        :param password: 密码
        :return:
        """
        self.logger.info("启动 ArkID 官方认证（用户名 + 密码）")
        body = {'username': username, 'password': password}
        self.__certification = self.post(path='login/', json_body=body)

    def get_token(self):
        """
        获取 oneid_token
        :return: ``oneid_token`` (*str*)
        """
        return self.__certification.get('token')

    def auth_to_get_token(self, _username: str, _password: str):
        """
        简化 oneid_token 的获取流程，大多数时候比传统的获取方式更轻松。
        :param _username: 用户唯一标识
        :param _password: 密码
        """
        self.start_auth(_username, _password)
        return self.get_token()

    @reload_authorizer
    @reload_service('revoke')
    def revoke_token(self, authorizer: BasicAuthorizer):
        """
        撤销 oneid_token
        :param authorizer: 特指 < BasicAuthorizer > 类型的授权器
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 ConfidentialAppAuthClient.revoke_token() 接口与 ArkID 服务端进行交互")
        return self.post(path='token/')

    @reload_authorizer
    @reload_service('auth')
    def auth_token(self, authorizer: BasicAuthorizer):
        """
        校验 oneid_token 所代表的用户是否有某特定权限
        :type authorizer: BasicAuthorizer
        :param authorizer: 特指 < BasicAuthorizer > 类型的授权器
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 ConfidentialAppAuthClient.auth_token() 接口与 ArkID 服务端进行交互")
        return self.get(path='token/')

    def get_authorizer(self, username: str, password: str):
        """
        封装 self.auth_to_get_token 方法，通过认证客户端直接
        获得有效的授权器
        :param username: 用户唯一标识
        :param password: 密码
        :return: :class: < BasicAuthorizer > object
        """
        return BasicAuthorizer(self.auth_to_get_token(username, password))
