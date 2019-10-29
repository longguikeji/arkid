'''
企业微信查询用户信息
'''
import requests

from thirdparty_data_sdk.wechat_sdk import constants


def get_union_id(code, appid, secret):
    '''
    查询用户id
    '''
    unionid = ''
    try:
        get_token_response = requests.get(constants.GET_TOKEN_URL,\
            params={'code':code, 'appid':appid, 'secret':secret, 'grant_type':'authorization_code'}).json()
        unionid = get_token_response['unionid']
    except Exception:    # pylint: disable=broad-except
        pass
    return unionid


def check_valid(appid, secret):    # pylint: disable=missing-function-docstring
    try:
        errcode = requests.get(constants.GET_TOKEN_URL,\
                params={'appid':appid, 'secret':secret, 'grant_type':'authorization_code'}).json()['errcode']
        if errcode == 41008:
            return True
        return False
    except Exception:    # pylint: disable=broad-except
        return False
