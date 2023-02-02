from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
    ExternalIdpBaseSchema,
)
from arkid.core.extension import create_extension_schema
from .constants import AUTHORIZE_URL, IMG_URL, GET_TOKEN_URL, GET_USERINFO_URL, KEY
from .models import DingdingUser
import requests
from urllib.parse import parse_qs, quote
import uuid
import json
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from arkid.config import get_app_config


class ConfigSchema(Schema):

    app_key: str = Field(title=_('App Key', '应用Key'))
    app_secret: str = Field(title=_('App Secret', '应用Secret'))

    img_url: str = Field(title=_('Img URL', '图标URL'), format='upload', default='')
    login_url: str = Field(title=_('Login URL', '登录URL'), readonly=True, default='')
    callback_url: str = Field(
        title=_('Callback URL', '回调URL'), readonly=True, default=''
    )
    bind_url: str = Field(title=_('Bind URL', '绑定URL'), readonly=True, default='')
    frontend_callback: str = Field(
        title=_('Frontend Callback URL', '前端跳转页面'), readonly=True, default=''
    )


DingdingConfigSchema = create_extension_schema(
    'DingdingConfigSchema', __file__, base_schema=ConfigSchema
)


class ExternalIdpDingdingExtension(ExternalIdpExtension):
    def load(self):
        super().load()
        self.register_extend_field(DingdingUser, "dingding_user_id")
        self.register_extend_field(DingdingUser, "dingding_nickname")
        self.register_extend_field(DingdingUser, "dingding_avatar")
        self.register_external_idp_schema("dingding", DingdingConfigSchema)

    def get_auth_code_from_request(self, request):
        code = request.GET.get("authCode", '')
        return code

    def get_img_url(self):
        """
        返回Github的图标URL
        """
        return IMG_URL

    def get_authorize_url(self, config, callback_url, next_url):
        """
        Args:
            client_id (str): 注册Github应用返回的客户端标识
            redirect_uri (str): 在ArkID中创建Github登录配置后返回的回调地址
        Returns:
            str: 返回用于向Github发起认证的URL
        """
        redirect_uri = quote(callback_url)
        url = AUTHORIZE_URL.format(
            redirect_uri, config.config.get("app_key"), uuid.uuid4().hex
        )
        return url

    def get_ext_token(self, config, code):
        """
        Args:
            config (arkid.extension.models.TenantExtensionConfig): 第三方认证提供的Client_ID,
            code (str): Github返回的授权码
        Returns:
            str: 返回Github返回的access_token
        """
        data = {
            "code": code,
            "clientId": config.config.get("app_key"),
            "clientSecret": config.config.get("app_secret"),
            "grantType": "authorization_code",
        }

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.post(
            GET_TOKEN_URL,
            headers=headers,
            data=json.dumps(data),
        )

        response = response.__getattribute__("_content").decode()
        result = json.loads(response)

        return result["accessToken"]

    def get_ext_user_info(self, config, code, token):
        """
        Args:
            token (str): Github返回的access_token
        Returns:
            tuple: 返回Github中用户信息中的id， login，avatar_url和所有用户信息
        """
        headers = {"x-acs-dingtalk-access-token": token}
        response = requests.get(
            GET_USERINFO_URL,
            headers=headers,
        ).json()
        # nick = response.get("nick", "")
        avatar = response.get("avatarUrl", "")
        mobile = response.get("mobile", "")
        openid = response.get("openId", "")
        # unionid = response.get("unionId", "")
        # email = response.get("email", "")
        return openid, mobile, avatar, response

    def get_arkid_user(self, ext_id):
        """
        Args:
            ext_id (str): 从Github用户信息接口获取的用户标识
        Returns:
            arkid.core.models.User: 返回ext_id绑定的ArkID用户
        """
        dingding_user = DingdingUser.valid_objects.filter(
            dingding_user_id=ext_id
        ).first()
        if dingding_user:
            return dingding_user.target
        else:
            return None

    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 从Github用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
            data (dict) request数据
        """
        user.dingding_user_id = ext_id
        user.dingding_nickname = data.get('ext_name', '')
        user.dingding_avatar = data.get('ext_icon', '')
        user.save()

    def get_img_and_redirect_url(self, config):
        return config.config.get("img_url", ""), config.config.get("login_url", "")


extension = ExternalIdpDingdingExtension()
