"""
WeChatScan查询用户信息
"""
from urllib.parse import parse_qs
import requests
import json

from . import constants


class APICallError(Exception):
    def __init__(self, error_info):
        super(APICallError, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return "API call error occur:" + self.error_info


# pylint: disable=line-too-long
# pylint: disable=consider-using-dict-comprehension
class WeChatScanUserInfoManager:
    """
    WeChatScan API
    """

    def __init__(self, appid, secret):
        self.appid = appid
        self.secret = secret

    def get_user_info(self, code):
        """
        查询用户id
        """
        try:
            response = requests.post(
                constants.GET_TOKEN_URL,
                params={
                    "code": code,
                    "appid": self.appid,
                    "secret": self.secret,
                    "grant_type": "authorization_code",
                },
            )

            response = response.__getattribute__("_content").decode()
            result = json.loads(response)
            access_token = result["access_token"]
            refresh_token = result["refresh_token"]
            openid = result["openid"]
            # unionid = result["unionid"]
            # 获取user info
            # {
            #     "access_token":"ea7d7cdfdeb0c8c986fdde9c371ae96d",
            #     "token_type":"bearer",
            #     "expires_in":86400,
            #     "refresh_token":"ffff7399095b206cbbdcc22da38dbfbea847db9528bc69cd6bf3e427cc6c736f",
            #     "scope":"user_info projects pull_requests issues notes keys hook groups gists enterprises emails",
            #     "created_at":1621943205
            # }
            headers = {"Authorization": "token " + access_token}
            response = requests.get(
                constants.GET_USERINFO_URL,
                params={
                    "access_token": access_token,
                    "openid": openid,
                },
            ).json()
            nickname = response.get("nickname", "")
            avatar = response.get("headimgurl", "")
            unionid = response.get("unionid", "")
            return openid, unionid, nickname, avatar, access_token, refresh_token
        except Exception as e:
            raise APICallError(e)
