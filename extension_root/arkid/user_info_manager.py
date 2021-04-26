"""
ArkID查询用户信息
"""
from config import get_app_config
import requests
import json


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
        # 获取access_token
        token_url = "{}/api/v1/tenant/{}/oauth/token/".format(c.get_host(), self.tenant_uuid)
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        response = requests.post(
            token_url,
            auth=auth,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "tenant_uuid": self.tenant_uuid,
            },
        )
        response = response.__getattribute__("_content").decode()
        result = json.loads(response)
        access_token = result["access_token"]
        # 获取user info
        user_info_url = "{}/api/v1/tenant/{}/userinfo/".format(c.get_host(), self.tenant_uuid)
        headers = {"Authorization": "bearer " + access_token}
        response = requests.get(
            user_info_url,
            headers=headers,
        )
        response = response.json()
        user_id = response["sub"]
        return user_id
