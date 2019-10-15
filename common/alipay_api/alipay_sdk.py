'''
站外API-调用阿里
'''
import logging

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipaySystemOauthTokenRequest import AlipaySystemOauthTokenRequest
from alipay.aop.api.response.AlipaySystemOauthTokenResponse import AlipaySystemOauthTokenResponse


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a',)
LOGGER = logging.getLogger('')

class AlipaySystemOauthTokenModel:
    '''
    模仿alipay包中的模型，用于在请求中放入参数，原包中竟然找不到对应接口的model，只能自己写一个
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
        授权码
        '''
        return self._code

    @code.setter
    def code(self, value):
        self._advance_payment_type = value


def get_alipay_id(auth_code, app_id, app_private_key, alipay_public_key):
    '''
    获取支付宝用户信息
    '''
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.url = 'https://openapi.alipaydev.com/gateway.do'
    alipay_client_config.app_id = app_id
    alipay_client_config.app_private_key = app_private_key
    alipay_client_config.alipay_public_key = alipay_public_key
    alipay_client_config.format = 'json'
    alipay_client_config.charset = 'utf-8'
    alipay_client_config.sign_type = 'RSA2'
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=LOGGER)

    model = AlipaySystemOauthTokenModel()
    model.grant_type = 'authorization_code'
    model.code = auth_code

    alipay_id_request = AlipaySystemOauthTokenRequest(biz_model=model)
    response_content = None
    try:
        response_content = client.execute(alipay_id_request)
    except Exception:    # pylint: disable=broad-except
        return {'err_msg':'get alipay id error'}
    if not response_content:
        return {'err_msg':'no response error'}
    res = AlipaySystemOauthTokenResponse()
    res.parse_response_content(response_content)
    if res.is_success():
        return res.user_id
    return {'err_msg':res.code + "," + res.msg + "," + res.sub_code + "," + res.sub_msg}
