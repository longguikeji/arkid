'''
站外API-调用阿里
'''
import time
import logging
import traceback

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayUserAuthUserinfoApplyModel import AlipayUserAuthUserinfoApplyModel
from alipay.aop.api.request.AlipaySystemOauthTokenRequest import AlipaySystemOauthTokenRequest
from alipay.aop.api.response.AlipaySystemOauthTokenResponse import AlipaySystemOauthTokenResponse
from oneid_meta.models.config import AlipayConfig



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a',)
logger = logging.getLogger('')


def get_alipay_id(auth_code, app_id, app_private_key, alipay_public_key):
    '''
    获取支付宝用户信息
    '''
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'
    alipay_client_config.app_id = app_id
    alipay_client_config.app_private_key = app_private_key
    alipay_client_config.alipay_public_key = alipay_public_key
    
    
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=logger)

    model = AlipayUserAuthUserinfoApplyModel()
    model.app_id = app_private_key
    model.auth_code = auth_code
    model.sign_type = 'RSA2'
    # model.timestamp = gen_time()
    model.charset = 'utf-8'
    alipay_id_request = AlipaySystemOauthTokenRequest(biz_model=model)
    response_content = None
    try:
        response_content = client.execute(alipay_id_request)
    except Exception:
        return {'err_msg':'get alipay id error'}
    if not response_content:
        return {'err_msg':'no response error'}
    else:
        res = AlipaySystemOauthTokenResponse()
        res.parse_response_content(response_content)
        print(res.body)
        if res.is_success():
            print("get user alipay_id:", res.user_id)
        else:
            print(res.code + "," + res.msg + "," + res.sub_code + "," + res.sub_msg)
    #     # 构造请求参数对象

    # request = AlipaySystemOauthTokenRequest()
    # request._code = auth_code
    # request._grant_type = "authorization_code"
    # response = alipay_client.execute(request)
    # print(response, '<======RES JSON=======')
    # return response

def gen_time():
    timestamp = time.time()
    time_local = time.localtime(timestamp)
    format_time = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return format_time
get_alipay_id('dsafdsafdsafda')
