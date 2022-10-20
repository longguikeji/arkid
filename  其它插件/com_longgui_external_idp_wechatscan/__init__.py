from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
    ExternalIdpBaseSchema,
)
from arkid.core.extension import create_extension_schema
from .constants import AUTHORIZE_URL, IMG_URL, GET_TOKEN_URL, GET_USERINFO_URL, KEY
from .models import WechatscanUser
import requests
from urllib.parse import parse_qs, quote
import uuid
import json
from arkid.core.translation import gettext_default as _
from .schema import WechatScanSchema


WechatscanConfigSchema = create_extension_schema(
    'WechatscanConfigSchema', __file__, base_schema=WechatScanSchema
)


class ExternalIdpWechatscanExtension(ExternalIdpExtension):
    @property
    def key(self):
        return KEY

    def load(self):
        super().load()
        self.register_extend_field(WechatscanUser, "wechatscan_user_id")
        self.register_extend_field(WechatscanUser, "wechatscan_nickname")
        self.register_extend_field(WechatscanUser, "wechatscan_avatar")
        self.register_external_idp_schema("wechatscan", WechatscanConfigSchema)

    def get_img_url(self):
        """
        返回Wechatscan的图标URL
        """
        return IMG_URL

    def get_auth_code_from_request(self, request):
        code = request.GET.get("code", '')
        return code

    def get_authorize_url(self, config, callback_url, next_url):
        """
        Args:
            config (arkid.extension.models.TenantExtensionConfig): 第三方认证提供的Client_ID,
            callback_url (str): 由ArkID提供的回调地址
            next_url (str): 前端传来的跳转地址
        Returns:
            str: 返回用于向Wechatscan发起认证的URL
        """
        redirect_uri = "{}{}".format(callback_url, next_url)
        redirect_uri = quote(redirect_uri)
        url = AUTHORIZE_URL.format(
            config.config.get("app_id"),
            redirect_uri,
            uuid.uuid4().hex,
        )
        return url

    def get_ext_token(self, config, code):
        """
        Args:
            code (str): Wechatscan返回的授权码
            config (dict): Wechatscan第三方登录的插件配置
        Returns:
            str: 返回Wechatscan返回的access_token
        """
        response = requests.post(
            GET_TOKEN_URL,
            params={
                "code": code,
                "appid": config.config.get("app_id"),
                "secret": config.config.get("app_secret"),
                "grant_type": "authorization_code",
            },
        )

        response = response.__getattribute__("_content").decode()
        result = json.loads(response)
        openid = result["openid"]
        # 写入openid
        config.openid = openid
        return result["access_token"]

    def get_ext_user_info(self, config, code, token):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): 第三方认证返回的code
            token (str): 第三方认证返回的token
        Returns:
            tuple: 返回Wechatscan中用户信息中的id， login，avatar_url和所有用户信息
        """
        headers = {"Authorization": "token " + token}
        response = requests.get(
            constants.GET_USERINFO_URL,
            params={
                "access_token": token,
                "openid": config.openid,
            },
        ).json()
        # nickname = response.get("nickname", "")
        # avatar = response.get("headimgurl", "")
        # unionid = response.get("unionid", "")
        return config.openid, '', '', response

    def get_arkid_user(self, ext_id):
        """
        Args:
            ext_id (str): 从Wechatscan用户信息接口获取的用户标识
        Returns:
            arkid.core.models.User: 返回ext_id绑定的ArkID用户
        """
        wechat_work_user = WechatscanUser.valid_objects.filter(
            wechatscan_user_id=ext_id
        ).first()
        if wechat_work_user:
            return wechat_work_user.target
        else:
            return None

    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 从Wechatscan用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
            data (dict) request数据
        """
        user.wechatscan_user_id = ext_id
        user.wechatscan_nickname = data.get('ext_name', '')
        user.wechatscan_avatar = data.get('ext_icon', '')
        user.save()

    def get_img_and_redirect_url(self, config):
        return config.config.get("img_url", ""), config.config.get("login_url", "")


extension = ExternalIdpWechatscanExtension()
