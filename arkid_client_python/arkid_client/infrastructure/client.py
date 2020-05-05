"""
Define InfrastructureClient
"""
from arkid_client.authorizers import BasicAuthorizer, NullAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import InfrastructureAPIError, ArkIDSDKUsageError
from arkid_client.response import ArkIDHTTPResponse


class InfrastructureClient(BaseClient):
    """
    基础设施管理客户端，用于与 ArkID 服务端基础设施管理相关
    接口的访问操作。

    **Methods**

    *  :py:meth:`.get_sms_captcha`
    *  :py:meth:`.verify_sms_captcha`
    """
    allowed_authorizer_types = [BasicAuthorizer, NullAuthorizer]
    error_class = InfrastructureAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "infrastructure", authorizer=authorizer, **kwargs)

    def get_sms_captcha(self, action: str, mobile: str, **kwargs):
        """
        获取短信验证码
        操作包括：注册、登录、重置密码、激活账号、重置手机、通用
        (``POST /siteapi/v1/service/sms/*/``)

        **Parameters**:

            ``action`` (*str*)
              1）register (*注册*)
              2）login (*登录*)
              3）reset_password (*重置密码*)
              4）activate_user (*激活账号*)
              5）update_mobile (*重置手机*)
              6) general (*通用*)

            ``mobile`` (*str*)
              手机号

        **Examples**

        >>> ic = arkid_client.InfrastructureClient(...)
        >>> node = ic.get_sms_captcha('register', 'example')
        """
        actions_map = {
            'register': 'sms/register/',
            'login': 'sms/login/',
            'reset_password': 'sms/reset_password/',
            'activate_user': 'sms/activate_user/',
            'update_mobile': 'sms/update_mobile/',
            'general': 'sms/',
        }
        if action not in actions_map:
            self.logger.info("无法发送验证码， 暂不支持的操作类型")
            raise ArkIDSDKUsageError('无法为您发送验证码，暂不支持的操作类型(invalid action)')
        kwargs.update(mobile=mobile)
        self.logger.info("正在调用 InfrastructureClient.get_sms_captcha(action={}) 接口与 ArkID 服务端进行交互".
                         format(action))
        return self.post(path=actions_map[action], json_body=kwargs)

    def verify_sms_captcha(self, action: str, mobile: str, code: str):
        """
        验证短信验证码
        操作包括：注册、登录、重置密码、激活账号、重置手机、通用
        (``GET /siteapi/v1/service/sms/*/``)

        **Parameters**:

            ``action`` (*str*)
              1）register (*注册*)
              2）login (*登录*)
              3）reset_password (*重置密码*)
              4）activate_user (*激活账号*)
              5）update_mobile (*重置手机*)
              6) general (*通用*)

            ``mobile`` (*str*)
              手机号

        **Examples**

        >>> ic = arkid_client.InfrastructureClient(...)
        >>> node = ic.verify_sms_captcha('register', 'example')
        """
        actions_map = {
            'register': 'sms/register/',
            'login': 'sms/login/',
            'reset_password': 'sms/reset_password/',
            'activate_user': 'sms/activate_user/',
            'update_mobile': 'sms/update_mobile/',
            'general': 'sms/',
        }
        if action not in actions_map:
            self.logger.info("无法验证验证码， 暂不支持的操作类型")
            raise ArkIDSDKUsageError('无法为您验证验证码，暂不支持的操作类型(invalid action)')
        params = {'mobile': mobile, 'code': code}
        self.logger.info("正在调用 InfrastructureClient.verify_sms_captcha(action={}) 接口与 ArkID 服务端进行交互".
                         format(action))
        return self.get(path=actions_map[action], params=params)
