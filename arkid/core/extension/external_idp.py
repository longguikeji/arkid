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
        pass

    def login(self, request, tenant_id, config_id):
        """
        处理前端登录页面，点击第三方登录按钮的逻辑
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
    def get_ext_token_by_code(self, code):
        pass

    @abstractmethod
    def get_user_info_by_ext_token(self, token):
        pass

    @abstractmethod
    def get_ext_user(self, ext_id):
        pass

    def get_token(self, ext_id, tenant, configs):
        ext_user = self.get_ext_user(ext_id)
        if ext_user:
            user = ext_user.user
            token = refresh_token(user)
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
        处理第三方身份源的回调逻辑
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

    def get_img_url(self):
        """
        返回第三方登录按钮的图片
        """
        pass

    def register_external_idp_schema(self, idp_type, schema):
        self.register_config_schema(schema, self.package + '_' + idp_type)
        self.register_composite_config_schema(
            schema, idp_type, exclude=['extension']
        )

    def create_tenant_config(
        self, tenant, config, name, type 
    ):
        config_created = super().create_tenant_config(
            tenant, config, name, type
        )
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
