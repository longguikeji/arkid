"""
Dingding token manager get through appkey and appsecret or through corpid and corpsecret
"""

import time
import requests
from thirdparty_data_sdk.dingding.dingsdk import constants
from thirdparty_data_sdk.dingding.dingsdk.error_utils import APICallError

class AccessTokenManager():
    """
    class to init and hold access token
    """
    def __init__(self, app_key, app_secret, token_version=constants.TOKEN_FROM_APPKEY_APPSECRET):
        """
        :param token_version: =1 TOKEN_FROM_CORPID_CORPSECRET:gettoken through corpid and corpsecret;
                =2 TOKEN_FROM_APPKEY_APPSECRET:gettoken through app_key and app_secret
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.token_version = token_version
        self.access_token = None
        self.expired_time = None

    def get_access_token(self):
        """
        :return: usable token after necessary out of date refresh
        """
        if not self.access_token or int(self.expired_time) <= time.time():
            self.access_token = self.refresh_token()

        return self.access_token

    def refresh_token(self):
        """
        :return: token after necessary refresh and update expire time
        """
        if self.token_version == constants.TOKEN_FROM_CORPID_CORPSECRET:
            resp = requests.get(constants.ACCESS_TOKEN_URL,
                                params={
                                    'corpid': self.app_key,
                                    'corpsecret': self.app_secret
                                }).json()
        elif self.token_version == constants.TOKEN_FROM_APPKEY_APPSECRET:
            resp = requests.get(constants.ACCESS_TOKEN_URL,
                                params={
                                    'appkey': self.app_key,
                                    'appsecret': self.app_secret
                                }).json()
        elif self.token_version == constants.TOKEN_FROM_APPID_QR_APP_SECRET:
            resp = requests.get(constants.QR_GET_ACCESS_TOKEN_URL,
                                params={
                                    'appid': self.app_key,
                                    'appsecret': self.app_secret
                                }).json()
        else:
            raise APICallError('wrong param value token_version, value should be 1 or 2')

        errcode = resp.get('errcode', '')
        errmsg = resp.get('errmsg', '')

        if errcode != 0:
            raise APICallError('Failed to get the access token, code:%s, msg:%s' % (errcode, errmsg))

        self.access_token = resp.get('access_token', '')
        self.expired_time = int(time.time()) + constants.TOKEN_DURATION - constants.TOKEN_TOLERANCE_PERIOD

        return self.access_token
