'''
小程序查询用户信息
'''
# from urllib.parse import parse_qs
import requests

from . import constants


class APICallError(Exception):
    def __init__(self, error_info):
        super(APICallError, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return "API call error occur:" + self.error_info


# pylint: disable=line-too-long
# pylint: disable=consider-using-dict-comprehension
class MiniProgramUserInfoManager:
    '''
    MiniProgram API
    '''

    def __init__(self, app_id, secret_id):
        self.app_id = app_id
        self.secret_id = secret_id

    def get_user_id(self, code):
        '''
        查询用户id
        '''
        try:
            if code:
                url = constants.SESSION_URL.format(self.app_id, self.secret_id, code)
                response = requests.get(url)
                result = response.json()
                # import time
                # result = {
                #     "openid": str(int(time.time()))
                # }
            openid = result.get("openid")
            return openid
        except Exception:
            raise APICallError("Invalid auth_code")
