"""
Gitee查询用户信息
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
class GiteeUserInfoManager:
    """
    Gitee API
    """

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_user_id(self, code):
        """
        查询用户id
        """
        try:
            response = requests.post(
                constants.GET_TOKEN_URL,
                params={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )
            response = response.__getattribute__("_content").decode()
            result = json.loads(response)
            access_token = result["access_token"]
            refresh_token = result["refresh_token"]
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
                params={"access_token": access_token},
                headers=headers,
            ).json()
            user_id = response["id"]
            return user_id, access_token, refresh_token
        except Exception as e:
            raise APICallError(e)

    def check_valid(self):  # pylint: disable=missing-function-docstring
        try:
            response = requests.get(
                constants.GET_TOKEN_URL,
                params={
                    "code": "123",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                },
            ).__getattribute__("_content")
            result = dict(
                [(k, v[0]) for k, v in parse_qs(response.decode()).items()]
            )  # 将响应信息转换为字典
            if (
                result["error"] == constants.CLIENT_VALID
            ):  # client_id,client_secret正确情况下的error值
                return True
            return False
        except Exception:  # pylint: disable=broad-except
            return False
