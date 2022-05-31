from arkid.core.extension.external_idp import ExternalIdpExtension, ExternalIdpBaseSchema
from arkid.core.extension import create_extension_schema
from .constants import AUTHORIZE_URL, IMG_URL, GET_TOKEN_URL, GET_USERINFO_URL
from .models import GithubUser
import requests
from urllib.parse import parse_qs

package = 'com.longgui.external.idp.github'

GithubConfigSchema = create_extension_schema(
    'GithubConfigSchema', package, base_schema=ExternalIdpBaseSchema
)


class ExternalIdpGithubExtension(ExternalIdpExtension):
    def load(self):
        super().load()
        self.register_extend_field(GithubUser, "github_user_id")
        self.register_external_idp_schema(self.type, GithubConfigSchema)

    def get_img_url(self):
        return IMG_URL


    def get_authorize_url(self, client_id, redirect_uri):
        url = "{}?client_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            client_id,
            redirect_uri,
        )
        return url

    def get_ext_token_by_code(self, code, settings):
        response = requests.post(
                GET_TOKEN_URL,
                params={
                    "code": code,
                    "client_id": settings.get("client_id"),
                    "client_secret": settings.get("client_secret"),
                    "grant_type": "authorization_code",
                },
            ).__getattribute__("_content")
        result = dict(
            [(k, v[0]) for k, v in parse_qs(response.decode()).items()]
        )  # 将响应信息转换为字典
        return result["access_token"]

    def get_user_info_by_ext_token(self, token):
        # 获取user info
        headers = {"Authorization": "token " + token}
        response = requests.get(
            GET_USERINFO_URL,
            params={"access_token": token},
            headers=headers,
        ).json()
        return response["id"], response["login"], response["avatar_url"], response

    def get_arkid_user(self, ext_id):
        return GithubUser.valid_objects.filter(github_user_id=ext_id).first()

    def bind_arkid_user(self, ext_id, user):
        user.github_user_id = ext_id
        user.save()




extension = ExternalIdpGithubExtension(
    package=package,
    name='Github第三方登录服务',
    version='1.0',
    labels='external-idp-github',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
