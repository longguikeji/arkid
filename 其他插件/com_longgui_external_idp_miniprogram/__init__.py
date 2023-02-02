from arkid.core.extension.external_idp import (
    ExternalIdpExtension,
)
from arkid.core.translation import gettext_default as _
from arkid.core.extension import create_extension_schema
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import re_path
from arkid.config import get_app_config
from django.urls import reverse
from .models import MiniprogramUser
from arkid.core.token import refresh_token
from .schema import ExternalIdpMiniprogramSchema
from .error import ErrorCode
from .constants import *
import requests
import uuid
import json
from urllib.parse import parse_qs, quote


MiniprogramConfigSchema = create_extension_schema(
    'MiniprogramConfigSchema', __file__, base_schema=ExternalIdpMiniprogramSchema
)


class ExternalIdpMiniprogramExtension(ExternalIdpExtension):

    redirect_uri = ''

    def load(self):
        # 重写父类的load方法开始
        urls = [
            re_path(
                rf'^idp/{self.pname}/(?P<config_id>[\w-]+)/login$',
                self.login,
                name=f'{self.pname}_login',
            ),
            re_path(
                rf'^idp/{self.pname}/(?P<config_id>[\w-]+)/bind$',
                self.bind,
                name=f'{self.pname}_bind',
            ),
        ]
        self.register_routers(urls, False)
        # 小程序登录不出现的在登陆页
        # self.listen_event(
        #     core_event.CREATE_LOGIN_PAGE_AUTH_FACTOR, self.add_idp_login_buttons
        # )
        # 重写父类的load方法结束
        self.register_extend_field(MiniprogramUser, "miniprogram_user_id")
        self.register_extend_field(MiniprogramUser, "miniprogram_nickname")
        self.register_extend_field(MiniprogramUser, "miniprogram_avatar")
        self.register_external_idp_schema("miniprogram", MiniprogramConfigSchema)

    def login(self, request, config_id):
        code = request.GET.get("code", '')
        # name = request.GET.get("name")
        # avatar = request.GET.get("avatar")
        config = self.get_config_by_id(config_id)

        if not config:
            return JsonResponse(self.error(ErrorCode.LOGIN_CONFIG_NOT_FIND))
        if code == '':
            return JsonResponse(self.error(ErrorCode.CODE_IS_EMPTY))

        app_id = config.config.get("app_id")
        app_secret = config.config.get("app_secret")

        url = SESSION_URL.format(app_id, app_secret, code)
        response = requests.get(url)
        result = response.json()
        ext_id = result.get("openid")

        arkid_user = self.get_arkid_user(ext_id)
        if arkid_user:
            token = refresh_token(arkid_user)
            context = {"token": token}
        else:
            context = {
                "token": "",
                "ext_id": ext_id,
                "tenant_id": config.tenant.id.hex,
                "bind": config.config.get('bind_url'),
            }
        return JsonResponse(self.success(context))

    def get_img_url(self):
        """
        返回Miniprogram的图标URL
        """
        return ''

    def get_auth_code_from_request(self, request):
        '''
        不需要去request里拿
        '''
        pass

    def get_authorize_url(self, config, callback_url, next_url):
        """
        去拿授权地址
        """
        pass
    
    def callback(self, request, config_id):
        """
        不需要去回调
        """
        pass

    def get_ext_token(self, config, code):
        """
        不需要获取access_token
        """
        pass

    def get_ext_user_info(self, config, code, token):
        """
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): Miniprogram返回的授权码
            token (str): Miniprogram返回的access_token
        Returns:
            tuple: 返回Miniprogram中用户信息中的id， login，avatar_url和所有用户信息
        """
        pass

    def get_arkid_user(self, ext_id):
        """
        Args:
            ext_id (str): 从MiniprogramUser用户信息接口获取的用户标识
        Returns:
            arkid.core.models.User: 返回ext_id绑定的ArkID用户
        """
        miniprogram_user = MiniprogramUser.valid_objects.filter(miniprogram_user_id=ext_id).first()
        if miniprogram_user:
            return miniprogram_user.target
        else:
            return None

    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 从Miniprogram用户信息接口获取的用户标识
            user (arkid.core.models.User): 用于绑定的ArkID用户
            data (dict) request数据
        """
        user.miniprogram_user_id = ext_id
        user.miniprogram_nickname = data.get('ext_name', '')
        user.miniprogram_avatar = data.get('ext_icon', '')
        user.save()

    def get_img_and_redirect_url(self, config):
        pass

    def create_tenant_config(self, tenant, config, name, type):
        from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        config_created = TenantExtensionConfig.valid_objects.create(tenant=tenant, extension=ext, config=config, name=name, type=type)
        server_host = get_app_config().get_host()
        login_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_login',
            args=[config_created.id],
        )
        bind_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_bind',
            args=[config_created.id],
        )
        config["login_url"] = login_url
        config["bind_url"] = bind_url
        config_created.config = config
        config_created.save()
        return config_created


extension = ExternalIdpMiniprogramExtension()
