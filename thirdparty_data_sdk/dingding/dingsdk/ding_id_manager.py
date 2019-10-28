'''
从第三方获取user_id
'''
import requests
from thirdparty_data_sdk.dingding.dingsdk import constants
from thirdparty_data_sdk.dingding.dingsdk.error_utils import APICallError
from oneid_meta.models import DingConfig


class DingIdManager():
    '''
    从第三方获取user_id
    '''
    def __init__(self, code):
        self.code = code
        self.ding_id = None

    def get_ding_id(self):
        '''
        从钉钉获取dingId
        '''
        appid = DingConfig.get_current().qr_app_id
        appsecret = DingConfig.get_current().qr_app_secret
        access_token = requests.get(constants.QR_GET_ACCESS_TOKEN_URL, params={'appid':appid,\
            'appsecret':appsecret}).json()['access_token']
        get_psstt_code = requests.post(constants.QR_GET_PSSTT_CODE_URL, params={'access_token':access_token},\
            json={'tmp_auth_code':self.code})
        openid = get_psstt_code.json()['openid']
        persistent_code = get_psstt_code.json()['persistent_code']
        sns_token = requests.post(constants.QR_GET_SNS_TOKEN_URL, params={'access_token':access_token},\
            json={'openid':openid, 'persistent_code':persistent_code}).json()['sns_token']
        resp = requests.get(constants.QR_GET_USER_INFO_URL,\
            params={'sns_token': sns_token}).json()
        errcode = resp.get('errcode', '')
        errmsg = resp.get('errmsg', '')

        if errcode != 0:
            raise APICallError('Failed to get ding id,code:%s, msg:%s' % (errcode, errmsg))
        self.ding_id = resp.get('user_info', '')['dingId']
        return self.ding_id
