"""
Dingding token manager get through appkey and appsecret or through corpid and corpsecret
"""

from thirdparty_data_sdk.alipay_api import alipay_sdk
from thirdparty_data_sdk.alipay_api.error_utils import APICallError


class AlipayResManager():
    """
    class to init and hold access token
    """
    def __init__(self, app_id, app_private_key, alipay_public_key, auth_code=''):
        self.auth_code = auth_code
        self.app_id = app_id
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key

    def get_alipay_user_id(self):
        '''
        返回True 或 False
        '''
        try:
            user_id = alipay_sdk.get_alipay_user_id(auth_code=self.auth_code,\
            app_private_key=self.app_private_key, alipay_public_key=self.alipay_public_key, app_id=self.app_private_key)
        except:
            raise APICallError('get alipay user id failed')
        return user_id

    def check_config_valid(self):
        '''
        检查支付宝配置是否正确
        '''
        try:
            is_valid = alipay_sdk.check_valid(app_id=self.app_id,
                                              app_private_key=self.app_private_key,
                                              alipay_public_key=self.alipay_public_key)
        except:
            raise APICallError('check config valid failed')
        return is_valid
