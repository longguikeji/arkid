'''
钉钉API
'''
import requests
from oneid_meta.models import DingConfig


BASEURL = 'https://oapi.dingtalk.com/sns/'

def get_ding_id(code):
    '''
    从钉钉获取ding_id
    '''
    appid = DingConfig.get_current().qr_app_id
    appsecret = DingConfig.get_current().qr_app_secret
    access_token = requests.get(BASEURL + 'gettoken', params={'appid':appid,\
        'appsecret':appsecret}).json()['access_token']
    get_psstt_code = requests.post(BASEURL + 'get_persistent_code', params={'access_token':access_token},\
    json={'tmp_auth_code':code})
    openid = get_psstt_code.json()['openid']
    persistent_code = get_psstt_code.json()['persistent_code']
    sns_token = requests.post(BASEURL + 'get_sns_token', params={'access_token':access_token},\
    json={'openid':openid, 'persistent_code':persistent_code}).json()['sns_token']
    user_info = requests.get(BASEURL + 'getuserinfo', params={'sns_token': sns_token}).json()['user_info']
    user_ids = {'ding_id': user_info['dingId'], 'openid': user_info['openid'], 'unionid': user_info['unionid']}
    return user_ids

def get_access_token(qr_app_id, qr_app_secret):
    '''
    从钉钉获取access_token
    '''
    res = requests.get(BASEURL + 'gettoken', params={'appid':qr_app_id,\
        'appsecret':qr_app_secret}).json()
    print(res, '<======== RES ========')
    return res
