'''
站外API-调用阿里
'''
import traceback

from rest_framework.exceptions import ValidationError
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipaySystemOauthTokenRequest import AlipaySystemOauthTokenRequest
from alipay.aop.api.response.AlipaySystemOauthTokenResponse import AlipaySystemOauthTokenResponse
from alipay.aop.api.exception.Exception import AopException
from thirdparty_data_sdk.alipay_api import constants


class AlipaySystemOauthTokenModel:
    '''
    模仿alipay-sdk-python包中的模型，用于在请求中放入参数
    '''
    def __init__(self):
        self._grant_type = None
        self._code = None

    @property
    def grant_type(self):
        '''
        授权类型
        '''
        return self._grant_type

    @grant_type.setter
    def grant_type(self, value):
        self._grant_type = value

    @property
    def code(self):
        '''
        auth_code
        '''
        return self._code

    @code.setter
    def code(self, value):
        self._code = value

    def to_alipay_dict(self):
        '''
        将参数放入字典便于下一步alipay-sdk-python调用
        '''
        params = dict()
        if self.grant_type:
            if hasattr(self.grant_type, 'to_alipay_dict'):
                params['grant_type'] = self.grant_type.to_alipay_dict()
            else:
                params['grant_type'] = self.grant_type
        if self.code:
            if hasattr(self.code, 'to_alipay_dict'):
                params['code'] = self.code.to_alipay_dict()
            else:
                params['code'] = self.code
        return params


def get_alipay_oauth_token_response(app_id, app_private_key, alipay_public_key, auth_code=''):
    '''
    初始化一个支付宝请求client
    '''
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = constants.SERVER_URL
    alipay_client_config.app_id = app_id
    alipay_client_config.app_private_key = app_private_key
    alipay_client_config.alipay_public_key = alipay_public_key
    alipay_client_config.format = 'json'
    alipay_client_config.charset = 'utf-8'
    alipay_client_config.sign_type = 'RSA2'
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
    model = AlipaySystemOauthTokenModel()
    request = AlipaySystemOauthTokenRequest(biz_model=model)
    request.code = auth_code
    request.grant_type = 'authorization_code'
    response_content = None
    try:
        response_content = client.execute(request)
    except AopException:
        print(traceback.format_exc())
    if not response_content:
        raise ValidationError({'app_id|app_private_key|alipay_public_key': ['all should be correct']})
    res = AlipaySystemOauthTokenResponse()
    res.parse_response_content(response_content)
    return res


def check_valid(app_id, app_private_key, alipay_public_key):
    '''
    检查配置是否正确
    '''
    # 实例化客户端
    res = get_alipay_oauth_token_response(app_id=app_id, app_private_key=app_private_key,\
        alipay_public_key=alipay_public_key)
    if res.code == '40002':
        return True
    return False


def get_alipay_user_id(app_id, app_private_key, alipay_public_key, auth_code):
    '''
    获取支付宝用户信息
    '''
    # 实例化客户端
    res = get_alipay_oauth_token_response(app_id=app_id, app_private_key=app_private_key,\
        alipay_public_key=alipay_public_key, auth_code=auth_code)
    if res.is_success():
        return res.user_id
    raise ValidationError({'err_msg': res.code + ',' + res.msg})
