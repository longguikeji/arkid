"""
ArkID查询用户信息
"""
from config import get_app_config
from requests_oauthlib import OAuth2Session


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
        # 获取state
        authorization_base_url = "{}/api/v1/tenant/{}/oauth/authorize/".format(c.get_host(), self.tenant_uuid)
        github = OAuth2Session(self.client_id)
        authorization_url, state = github.authorization_url(authorization_base_url)
        # 获取授权token
        token_url = "{}/api/v1/tenant/{}/oauth/token/".format(c.get_host(), self.tenant_uuid)
        github = OAuth2Session(self.client_id, state=state)
        authorization_response_url = "{}/api/v1/tenant/{}/arkid/callback/?code={}&state={}".format(c.get_host(), self.tenant_uuid, code, state)
        print('>>>>', token_url, self.client_secret, authorization_response_url, state)
        token = github.fetch_token(
            token_url,
            client_secret=self.client_secret,
            authorization_response=authorization_response_url
        )
        # response = requests.post(
        #     token_url,
        #     auth=auth,
        #     params={
        #         "code": code,
        #         "client_id": self.client_id,
        #         "client_secret": self.client_secret,
        #         "grant_type": "authorization_code",
        #         "redirect_uri": self.redirect_uri,
        #     },
        # )
        # print(response)
