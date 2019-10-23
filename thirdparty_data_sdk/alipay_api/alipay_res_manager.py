"""
Dingding token manager get through appkey and appsecret or through corpid and corpsecret
"""

from thirdparty_data_sdk.alipay_api import constants
from thirdparty_data_sdk.alipay_api import alipay_sdk
from thirdparty_data_sdk.alipay_api.error_utils import APICallError


class AlipayResManager():
    """
    class to init and hold access token
    """
    def __init__(self,
                 app_id,
                 app_private_key,
                 alipay_public_key,
                 auth_code='',
                 requie_type=constants.CHECK_ID_SECRET_VALID):
        self.auth_code = auth_code
        self.app_id = app_id
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key
        self.requie_type = requie_type

    def get_alipay_id(self):
        '''
        返回True 或 False
        '''
        if self.auth_code == '':
            return self.alipay_api_response

    def alipay_api_response(self):
        """
        :return: alipay_id_res which includes id.
        """
        if self.requie_type == constants.CHECK_ID_SECRET_VALID:
            resp = alipay_sdk.alipay_api_response(app_id=self.app_id,
                                                  app_private_key=self.app_private_key,
                                                  alipay_public_key=self.alipay_public_key)
        else:
            raise APICallError('wrong param value token_version, value should be 1')

        errcode = resp.code

        return errcode
