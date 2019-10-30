'''
企业微信查询用户信息
'''
import requests
# from rest_framework.exceptions import ValidationError
from thirdparty_data_sdk.wechat_sdk import constants
from thirdparty_data_sdk.wechat_sdk.error_utils import APICallError


class WechatUserInfoManager:
    '''
    微信API
    '''
    def __init__(self, code, appid, secret):
        self.code = code
        self.appid = appid
        self.secret = secret

    def get_union_id(self):
        '''
        查询用户id
        '''
        try:
            get_token_response = requests.get(constants.GET_TOKEN_URL,\
                params={'code':self.code, 'appid':self.appid, 'secret':self.secret,\
                    'grant_type':'authorization_code'}).json()
            unionid = get_token_response['unionid']
            return unionid
        except Exception:
            raise APICallError('Invalid auth_code')

    def check_valid(self):    # pylint: disable=missing-function-docstring
        try:
            errcode = requests.get(constants.GET_TOKEN_URL,\
                    params={'appid':self.appid, 'secret':self.secret,\
                        'grant_type':'authorization_code'}).json()['errcode']
            if errcode == constants.MISSING_CODE:
                return True
            return False
        except Exception:    # pylint: disable=broad-except
            return False
