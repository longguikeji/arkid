from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
    ExternalIdpBaseSchema,
)
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
        """
        返回Github的图标URL
        """
        return IMG_URL

    def get_authorize_url(self, client_id, redirect_uri):
        """
        Args:
            client_id (str): 注册Github应用返回的客户端标识
            redirect_uri (str): 在ArkID中创建Github登录配置后返回的回调地址
        Returns:
            str: 返回用于向Github发起认证的URL
        """
        url = "{}?client_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            client_id,
            redirect_uri,
        )
        return url

    def get_ext_token_by_code(self, code, config):
        """
        Args:
            code (str): Github返回的授权码
            config (dict): Github第三方登录的插件配置
        Returns:
            str: 返回Github返回的access_token
        """
        response = requests.post(
            GET_TOKEN_URL,
            params={
                "code": code,
                "client_id": config.get("client_id"),
                "client_secret": config.get("client_secret"),
                "grant_type": "authorization_code",
            },
        ).__getattribute__("_content")
        result = dict(
            [(k, v[0]) for k, v in parse_qs(response.decode()).items()]
        )  # 将响应信息转换为字典
        return result["access_token"]

    def get_user_info_by_ext_token(self, token):
        """
        Args:
            token (str): Github返回的access_token
        Returns:
            tuple: 返回Github中用户信息中的id， login，avatar_url和所有用户信息
        """
        headers = {"Authorization": "token " + token}
        response = requests.get(
            GET_USERINFO_URL,
            params={"access_token": token},
            headers=headers,
        ).json()
        return response["id"], response["login"], response["avatar_url"], response

    def get_arkid_user(self, ext_id):
        """
        Args:
            ext_id (str): 从Github用户信息接口获取的用户标识
        Returns:
            arkid.core.models.User: 返回ext_id绑定的ArkID用户
        """
        return GithubUser.valid_objects.filter(github_user_id=ext_id).first().user

    def bind_arkid_user(self, ext_id, user):
        """
        Args:
            ext_id(str): 从Github用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
        """
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
