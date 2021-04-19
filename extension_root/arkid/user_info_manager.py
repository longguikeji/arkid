"""
ArkID查询用户信息
"""
from urllib.parse import parse_qs
from config import get_app_config
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
class ArkIDUserInfoManager:
    """
    ArkID API
    """

    def __init__(self, client_id, client_secret, redirect_uri, tenant_uuid):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tenant_uuid = tenant_uuid

    def get_user_id(self, code):
        """
        查询用户id
        """
        c = get_app_config()
        # # try:
        token_url = "{}/api/v1/tenant/{}/oauth/token/".format(c.get_host(), self.tenant_uuid)
        response = requests.post(
            token_url,
            params={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
        )
        print(response)

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
