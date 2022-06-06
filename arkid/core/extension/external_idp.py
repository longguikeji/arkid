#!/usr/bin/env python3
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.extension import RootSchema, create_extension_schema
from arkid.common.logger import logger
from django.urls import reverse
from arkid.config import get_app_config
from django.urls import re_path
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from arkid.core.token import refresh_token
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode, unquote
from arkid.common.utils import verify_token


class ExternalIdpBaseSchema(Schema):
    client_id: str = Field(title=_('Client ID', '客户端ID'))
    client_secret: str = Field(title=_('Client Secret', '客户端密钥'))
    img_url: str = Field(title=_('Img URL', '图标URL'), readonly=True, default='')
    login_url: str = Field(title=_('Login URL', '登录URL'), readonly=True, default='')
    callback_url: str = Field(
        title=_('Callback URL', '回调URL'), readonly=True, default=''
    )
    bind_url: str = Field(title=_('Bind URL', '绑定URL'), readonly=True, default='')


class ExternalIdpExtension(Extension):
    TYPE = "external_idp"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return ExternalIdpExtension.TYPE

    def load(self):

        urls = [
            re_path(
                rf'^idp/{self.pname}/(?P<config_id>[\w-]+)/login$',
                self.login,
                name=f'{self.pname}_login',
            ),
            re_path(
                rf'^idp/{self.pname}/(?P<config_id>[\w-]+)/callback$',
                self.callback,
                name=f'{self.pname}_callback',
            ),
            re_path(
                rf'^idp/{self.pname}/(?P<config_id>[\w-]+)/bind$',
                self.bind,
                name=f'{self.pname}_bind',
            ),
        ]
        self.register_routers(urls, True)
        super().load()

    @abstractmethod
    def get_authorize_url(self, client_id, redirect_uri):
        """
        抽象方法
        Args:
            client_id (str): 第三方认证提供的Client_ID,
            redirect_uri (str): 由ArkID提供的回调地址
        Returns:
            str: 第三方登录提供的认证URL
        """
        pass

    def login(self, request, tenant_id, config_id):
        """
        重定向到第三方登录的入口地址, 该入口地址由get_authorize_url提供
        """
        config = self.get_config_by_id(config_id)
        if not config:
            return JsonResponse({"error_msg": "没有找到登录配置"})
        config = config.config
        callback_url = config.get("callback_url")
        client_id = config.get("client_id")
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + next_url
        else:
            next_url = ""
        redirect_uri = "{}{}".format(callback_url, next_url)
        url = self.get_authorize_url(client_id, redirect_uri)

        return HttpResponseRedirect(url)

    @abstractmethod
    def get_ext_token_by_code(self, code, config):
        """
        抽象方法
        Args:
            code (str): 第三方认证返回的code
            config (dict): 第三方登录的插件运行时配置
        Returns:
            str: 返回第三方认证提供的token
        """
        pass

    @abstractmethod
    def get_user_info_by_ext_token(self, token):
        """
        抽象方法
        Args:
            token (str): 第三方认证返回的token
        Returns:
            dict: 返回第三方认证提供的用户信息
        """
        pass

    @abstractmethod
    def get_arkid_user(self, ext_id):
        """
        抽象方法
        Args:
            ext_id (str): 第三方认证返回的用户标识
        Returns:
            arkid.core.models.User: ArkID用户
        """
        pass

    def get_token(self, ext_id, tenant, configs):
        arkid_user = self.get_arkid_user(ext_id)
        if arkid_user:
            token = refresh_token(arkid_user)
            context = {"token": token}
        else:
            context = {
                "token": "",
                "ext_id": ext_id,
                "tenant_id": tenant.id,
                "bind": configs.get('callback_url'),
            }

        return context

    def callback(self, request, tenant_id, config_id):
        """
        拿到请求中携带的code，调用get_ext_token_by_code获取第三方认证的token，
        调用get_user_info_by_ext_token获取第三方认证提供的用户信息，
        拿到ext_id后，判断该ext_id是否已经和ArkID中的用户绑定，如果绑定直接返回绑定用户的Token，
        如果没有，返回重定向到前端绑定页面
        """
        code = request.GET["code"]
        next_url = request.GET.get("next", None)
        frontend_host = (
            get_app_config()
            .get_frontend_host()
            .replace('http://', '')
            .replace('https://', '')
        )
        if "third_part_callback" not in next_url or frontend_host not in next_url:
            return JsonResponse({'error_msg': '错误的跳转页面'})
        if code:
            try:
                config = self.get_config_by_id(config_id)
                config = config.config
                ext_token = self.get_ext_token_by_code(code, config)
                ext_id, ext_name, ext_icon, ext_info = self.get_user_info_by_ext_token(
                    ext_token
                )
            except Exception as e:
                logger.error(e)
                return JsonResponse({"error_msg": "授权码失效", "code": ["invalid"]})
        else:
            return JsonResponse({"error_msg": "授权码丢失", "code": ["required"]})

        context = self.get_token(ext_id, request.tenant, config)
        if next_url:
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)
        return JsonResponse(context)

    @abstractmethod
    def bind_arkid_user(self, ext_id, user):
        """
        Args:
            ext_id (str): 第三方登录返回的用户标识
            user (arkid.core.models.User): ArkID的用户
        Returns:
            {"token":xxx}: 返回token
        """
        pass

    @csrf_exempt
    def bind(self, request, tenant_id, config_id):
        """
        处理第三方身份源返回的user_id和ArkID的user之间的绑定
        """
        pass
        ext_id = request.POST.get("ext_id")
        user = verify_token(request)
        if not user:
            return JsonResponse({"error_msg": "Token验证失败", "code": ["token invalid"]})
        self.bind_arkid_user(ext_id, user)
        token = refresh_token(user)
        data = {"token": token}
        return JsonResponse(data)

    @abstractmethod
    def get_img_url(self):
        """
        抽象方法

        Returns:
            url str: 返回第三方登录按钮的图标
        """
        pass

    def register_external_idp_schema(self, idp_type, schema):
        self.register_config_schema(schema, self.package + '_' + idp_type)
        self.register_composite_config_schema(schema, idp_type, exclude=['extension'])

    def create_tenant_config(self, tenant, config, name, type):
        config_created = super().create_tenant_config(tenant, config, name, type)
        server_host = get_app_config().get_host()
        login_url = server_host + reverse(
            f'api:{self.pname}_tenant:{self.pname}_login',
            args=[tenant.id, config_created.id],
        )
        callback_url = server_host + reverse(
            f'api:{self.pname}_tenant:{self.pname}_callback',
            args=[tenant.id, config_created.id],
        )
        bind_url = server_host + reverse(
            f'api:{self.pname}_tenant:{self.pname}_bind',
            args=[tenant.id, config_created.id],
        )
        img_url = self.get_img_url()
        config["login_url"] = login_url
        config["callback_url"] = callback_url
        config["bind_url"] = bind_url
        config["img_url"] = img_url
        config_created.config = config
        config_created.save()
        return config_created
