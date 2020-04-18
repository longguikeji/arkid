'''
企业微信查询用户信息
'''
import requests
from ...thirdparty_data_sdk.wechat_sdk import constants
from ...thirdparty_data_sdk.error_utils import APICallError


class WechatUserInfoManager:
    '''
    微信API
    '''
    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret

    def get_union_id(self, code):
        '''
        查询用户id
        '''
        try:
            token_info = requests.get(constants.GET_TOKEN_URL,\
                params={'code':code, 'appid':self.appid, 'secret':self.secret,\
                    'grant_type':'authorization_code'}).json()
            unionid = token_info['unionid']
            return unionid
        except Exception:
            raise APICallError('Invalid auth_code')

    def check_valid(self):    # pylint: disable=missing-function-docstring
        try:
            errcode = requests.get(constants.GET_TOKEN_URL,\
                    params={'code':'123', 'appid':self.appid, 'secret':self.secret,\
                        'grant_type':'authorization_code'}).json()['errcode']
            if errcode == constants.APPID_SECRET_VALID:    # appid,secret正确情况下的errcode
                return True
            return False
        except Exception:    # pylint: disable=broad-except
            return False
