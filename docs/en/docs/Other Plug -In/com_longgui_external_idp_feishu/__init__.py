from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
)
from arkid.core.translation import gettext_default as _
from arkid.core.extension import create_extension_schema
from .constants import *
from .models import FeishuUser
from .schema import ExternalIdpFeishuSchema
import requests
import uuid
import json
from urllib.parse import parse_qs, quote



FeishuConfigSchema = create_extension_schema(
    'FeishuConfigSchema', __file__, base_schema=ExternalIdpFeishuSchema
)


class ExternalIdpFeishuExtension(ExternalIdpExtension):

    redirect_uri = ''

    def load(self):
        super().load()
        self.register_extend_field(FeishuUser, "feishu_user_id")
        self.register_extend_field(FeishuUser, "feishu_nickname")
        self.register_extend_field(FeishuUser, "feishu_avatar")
        self.register_external_idp_schema("feishu", FeishuConfigSchema)

    def get_img_url(self):
        """
        返回Feishu的图标URL
        """
        return IMG_URL

    def get_auth_code_from_request(self, request):
        code = request.GET.get("code", '')
        return code

    def get_authorize_url(self, config, callback_url, next_url):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            redirect_uri (str): 在ArkID中创建Feishu登录配置后返回的回调地址
        Returns:
            str: 返回用于向Feishu发起认证的URL
        """
        redirect_uri = "{}{}".format(callback_url, next_url)
        self.redirect_uri = redirect_uri
        redirect_uri = quote(redirect_uri)

        url = "{}?app_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            config.config.get("app_id"),
            redirect_uri,
            # str(uuid.uuid1().hex)
        )
        return url

    def get_ext_token(self, config, code):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): Feishu返回的授权码
        Returns:
            str: 返回Feishu返回的access_token
        """
        url = GET_TENANT_ACCESS_TOKEN
        r = requests.post(url, data={
            'app_id': config.config.get("app_id"),
            'app_secret': config.config.get("app_secret"),
        })
        data = r.json()
        token = data['tenant_access_token']
        return token

    def get_ext_user_info(self, config, code, token):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): Feishu返回的授权码
            token (str): Feishu返回的access_token
        Returns:
            tuple: 返回Feishu中用户信息中的id， login，avatar_url和所有用户信息
        """
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        data = {
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(
            GET_TOKEN_URL,
            headers=headers,
            data=json.dumps(data),
        )
        response = response.json()
        response = response.get("data")
        return response["user_id"], response["name"], response["avatar_url"], response

    def get_arkid_user(self, ext_id):
        """
        Args:
            ext_id (str): 从FeishuUser用户信息接口获取的用户标识
        Returns:
            arkid.core.models.User: 返回ext_id绑定的ArkID用户
        """
        feishu_user = FeishuUser.valid_objects.filter(feishu_user_id=ext_id).first()
        if feishu_user:
            return feishu_user.target
        else:
            return None

    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 从Feishu用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
            data (dict) request数据
        """
        user.feishu_user_id = ext_id
        user.feishu_nickname = data.get('ext_name', '')
        user.feishu_avatar = data.get('ext_icon', '')
        user.save()

    def get_img_and_redirect_url(self, config):
        return config.config.get("img_url", ""), config.config.get("login_url", "")


extension = ExternalIdpFeishuExtension()
