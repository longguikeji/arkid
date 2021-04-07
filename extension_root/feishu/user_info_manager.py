'''
飞书查询用户信息
'''
# from urllib.parse import parse_qs
# import requests

# from . import constants


class APICallError(Exception):
    def __init__(self, error_info):
        super(APICallError, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return "API call error occur:" + self.error_info


# pylint: disable=line-too-long
# pylint: disable=consider-using-dict-comprehension
class FeishuUserInfoManager:
    '''
    Feishu API
    '''

    def __init__(self, app_id, secret_id, app_access_token):
        self.app_id = app_id
        self.secret_id = secret_id
        self.app_access_token = app_access_token

    def get_user_id(self, code, next):
        '''
        查询用户id
        '''
        try:
            response = requests.post(
                constants.GET_TOKEN_URL,
                headers={
                    'Authorization': f'Bearer {self.app_access_token}',
                }
                params={
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            result = response.json()
            '''
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "access_token": "u-6U1SbDiM6XIH2DcTCPyeub",
                    "avatar_url": "www.feishu.cn/avatar/icon",
                    "avatar_thumb": "www.feishu.cn/avatar/icon_thumb",
                    "avatar_middle": "www.feishu.cn/avatar/icon_middle",
                    "avatar_big": "www.feishu.cn/avatar/icon_big",
                    "expires_in": 7140,
                    "name": "zhangsan",
                    "en_name": "Three Zhang",
                    "open_id": "ou-caecc734c2e3328a62489fe0648c4b98779515d3",
                    "union_id": "on_xxx",
                    "email": "zhangsan@feishu.cn",
                    "user_id": "5d9bdxx",
                    "mobile": "+86130xxx",
                    "tenant_key": "736588c92lxf175d",
                    "refresh_expires_in": 2591940,
                    "refresh_token": "ur-t9HHgRCjMqGqIU9v05Zhos",
                    "token_type": "Bearer"
                }
            }
            '''
            user_id = result.get("date").get("user_id")
            return user_id
        except Exception:
            raise APICallError("Invalid auth_code")
