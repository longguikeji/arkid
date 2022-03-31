"""
ArkID 查询用户信息
"""
import requests


class APICallError(Exception):
    def __init__(self, error_info):
        super(APICallError, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return "API call error occur:" + self.error_info


class ArkIDUserInfoManager:
    """
    ArkID API
    """

    def __init__(self, provider, tenant_uuid):
        self.client_id = provider.client_id
        self.client_secret = provider.client_secret
        self.redirect_uri = provider.callback_url
        self.token_url = provider.token_url
        self.userinfo_url = provider.userinfo_url
        self.tenant_uuid = tenant_uuid

    def get_user_info(self, code):
        """
        获取用户信息
        """
        # 获取access_token
        response = requests.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            ).json()
        access_token = response["access_token"]

        # 获取user info
        headers = {"Authorization": "bearer " + access_token}
        response = requests.get(
            self.userinfo_url,
            headers=headers,
        ).json()
        return response
