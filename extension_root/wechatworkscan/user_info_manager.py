"""
WeChatWorkScan查询用户信息
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
class WeChatWorkScanUserInfoManager:
    """
    WeChatWorkScan API
    """

    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret

    def get_user_info(self, code):
        """
        查询用户id
        """
        try:
            response = requests.get(constants.GET_TOKEN_URL.format(self.corpid,self.corpsecret))

            response = response.__getattribute__("_content").decode()
            result = json.loads(response)
            access_token = result["access_token"]
            response = requests.get(
                constants.GET_USERINFO_URL.format(access_token, code)
            ).json()
            device_id = response.get("DeviceId", "")
            work_user_id = response.get("UserId", "")

            return access_token, device_id, work_user_id
        except Exception as e:
            raise APICallError(e)
