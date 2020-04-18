'''
qq API
'''
import re
import requests
from ...thirdparty_data_sdk.qq_sdk import constants
from ...thirdparty_data_sdk.error_utils import APICallError


class QQInfoManager():
    '''
    调用qq接口获取用户信息
    '''
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_open_id(self, code):
        '''
        获取qq的openid
        '''
        try:
            access_token_response = requests.get(constants.GET_TOKEN_URL, params={'grant_type':'authorization_code',\
                'client_id':self.app_id, 'client_secret':self.app_key, 'code':code,\
                    'redirect_uri':constants.REDIRECT_URI}).text
            access_token = re.findall(r'access_token=(.*?)&', access_token_response)[0]
            open_id_response = requests.get(constants.GET_OPENID_URL, params={'access_token': access_token}).text
            open_id = re.findall(r'"openid":"(.*?)"}', open_id_response)[0]
        except Exception:    # pylint: disable=broad-except
            raise APICallError('invalid code')
        return open_id

    def check_config_valid(self):    # pylint: disable=no-self-use
        '''
        检查配置是否正确
        '''
        try:
            accesss_token_info = requests.get(constants.GET_TOKEN_URL, params={'grant_type':'authorization_code',\
                'client_id':self.app_id, 'client_secret':self.app_key, 'redirect_uri': constants.REDIRECT_URI}).text
            errcode = re.findall(r'"error":(.*?),', accesss_token_info)[0]
            if errcode == constants.APPID_KEY_VALID:
                return True
            return False
        except APICallError:    # pylint: disable=broad-except
            return False
