"""
Dingding token manager get through appkey and appsecret or through corpid and corpsecret
"""

from thirdparty_data_sdk.alipay_api import constants
from thirdparty_data_sdk.alipay_api import alipay_sdk


class AlipayResManager():
    """
    class to init and hold access token
    """
    def __init__(self,
                 app_id,
                 app_private_key,
                 alipay_public_key,
                 auth_code='',
                 token_version=constants.RES_FROM_ALIPAY):
        """
        :param token_version: =1 TOKEN_FROM_CORPID_CORPSECRET:gettoken through corpid and corpsecret;
                =2 TOKEN_FROM_APPKEY_APPSECRET:gettoken through app_key and app_secret
        """
        self.auth_code = auth_code
        self.app_id = app_id
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key
        self.token_version = token_version

    def get_alipay_id(self):
        '''
        返回True 或 False
        '''
        if self.auth_code == '':
            return self.get_alipay_id_res

    def get_alipay_id_res(self):
        """
        :return: alipay_id_res which includes id.
        """
        if self.token_version == constants.RES_FROM_ALIPAY:
            resp = alipay_sdk.get_alipay_id_res(app_id=self.app_id,
                                                app_private_key=self.app_private_key,
                                                alipay_public_key=self.alipay_public_key)
        else:
            raise Exception('wrong param value token_version, value should be 1')

        errcode = resp.code

        return errcode
