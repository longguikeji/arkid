'''
企业微信查询用户信息
'''
import requests

from thirdparty_data_sdk.work_wechat_sdk import constants


def get_work_wechat_user_id(code, corp_id, secret):
    '''
    查询用户id
    '''
    work_wechat_user_id = ''
    try:
        get_token_response = requests.get(constants.GET_TOKEN_URL,\
            params={'corpid':corp_id, 'corpsecret':secret}).json()
        print(get_token_response)
        access_token = get_token_response['access_token']
        get_user_id_response = requests.get(constants.GET_USERINFO_URL,\
            params={'access_token':access_token, 'code':code}).json()
        print(get_user_id_response)
        work_wechat_user_id = get_user_id_response['UserId']
    except Exception:    # pylint: disable=broad-except
        pass
    return work_wechat_user_id


def check_valid(corp_id, secret):    # pylint: disable=missing-function-docstring
    try:
        get_token_errcode = requests.get(constants.GET_TOKEN_URL,\
                params={'corpid':corp_id, 'corpsecret':secret}).json()['errcode']
        if get_token_errcode == 0:
            return True
        return False
    except Exception:    # pylint: disable=broad-except
        return False
