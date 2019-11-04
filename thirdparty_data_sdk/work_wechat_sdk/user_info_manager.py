'''
企业微信查询用户信息
'''
import requests
from thirdparty_data_sdk.work_wechat_sdk import constants
from thirdparty_data_sdk.error_utils import APICallError


class WorkWechatManager:
    '''
    企业微信查询接口
    '''
    def __init__(self, corp_id, secret):
        self.corp_id = corp_id
        self.secret = secret

    def get_work_wechat_user_id(self, code):
        '''
        查询用户id
        '''
        try:
            token_info = requests.get(constants.GET_TOKEN_URL,\
                params={'corpid':self.corp_id, 'corpsecret':self.secret}).json()
            access_token = token_info['access_token']
            user_info = requests.get(constants.GET_USERINFO_URL,\
                params={'access_token':access_token, 'code':code}).json()
            work_wechat_user_id = user_info['UserId']
            return work_wechat_user_id
        except Exception:
            raise APICallError('Failed to get the user id')

    def check_valid(self):    # pylint: disable=missing-function-docstring
        try:
            token_errcode = requests.get(constants.GET_TOKEN_URL,\
                    params={'corpid':self.corp_id, 'corpsecret':self.secret}).json()['errcode']
            if token_errcode == 0:
                return True
            return False
        except Exception:    # pylint: disable=broad-except
            return False
