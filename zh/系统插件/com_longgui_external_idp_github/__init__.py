from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
    ExternalIdpBaseSchema,
)
from arkid.core.extension import create_extension_schema
from .constants import AUTHORIZE_URL, IMG_URL, GET_TOKEN_URL, GET_USERINFO_URL, KEY
from .models import GithubUser
import requests
from urllib.parse import parse_qs, quote


GithubConfigSchema = create_extension_schema(
    'GithubConfigSchema', __file__, base_schema=ExternalIdpBaseSchema
)


class ExternalIdpGithubExtension(ExternalIdpExtension):
    def load(self):
        super().load()
        self.register_extend_field(GithubUser, "github_user_id")
        self.register_extend_field(GithubUser, "github_nickname")
        self.register_extend_field(GithubUser, "github_avatar")
        self.register_external_idp_schema("github", GithubConfigSchema)

    def get_img_url(self):
        """
        返回Github的图标URL
        """
        return IMG_URL

    def get_auth_code_from_request(self, request):
        code = request.GET.get("code", '')
        return code

    def get_authorize_url(self, config, callback_url, next_url):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            redirect_uri (str): 在ArkID中创建Github登录配置后返回的回调地址
        Returns:
            str: 返回用于向Github发起认证的URL
        """
        redirect_uri = "{}{}".format(callback_url, next_url)
        redirect_uri = quote(redirect_uri)
        url = "{}?client_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            config.config.get("client_id"),
            redirect_uri,
        )
        return url

    def get_ext_token(self, config, code):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): Github返回的授权码
        Returns:
            str: 返回Github返回的access_token
        """
        response = requests.post(
            GET_TOKEN_URL,
            params={
                "code": code,
                "client_id": config.config.get("client_id"),
                "client_secret": config.config.get("client_secret"),
                "grant_type": "authorization_code",
            },
        ).__getattribute__("_content")
        result = dict(
            [(k, v[0]) for k, v in parse_qs(response.decode()).items()]
        )  # 将响应信息转换为字典
        return result["access_token"]

    def get_ext_user_info(self, config, code, token):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): Github返回的授权码
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
        github_user = GithubUser.valid_objects.filter(github_user_id=ext_id).first()
        if github_user:
            return github_user.target
        else:
            return None

    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 从Github用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
            data (dict) request数据
        """
        user.github_user_id = ext_id
        user.github_nickname = data.get('ext_name', '')
        user.github_avatar = data.get('ext_icon', '')
        user.save()

    def get_img_and_redirect_url(self, config):
        return config.config.get("img_url", ""), config.config.get("login_url", "")


extension = ExternalIdpGithubExtension()
