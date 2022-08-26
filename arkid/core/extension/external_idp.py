#!/usr/bin/env python3
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.extension import RootSchema, create_extension_schema_by_package
from arkid.common.logger import logger
from django.urls import reverse
from arkid.config import get_app_config
from django.urls import re_path
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from arkid.core.token import refresh_token
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode, unquote
from arkid.common.utils import verify_token
from arkid.core import event as core_event


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
        self.register_routers(urls, False)
        self.listen_event(
            core_event.CREATE_LOGIN_PAGE_AUTH_FACTOR, self.add_idp_login_buttons
        )
        self.listen_event(
            core_event.ACCOUNT_UNBIND, self.account_unbind
        )
        super().load()

    @abstractmethod
    def get_authorize_url(self, config, callback_url, next_url):
        """
        抽象方法
        Args:
            config (arkid.extension.models.TenantExtensionConfig): 第三方认证提供的Client_ID,
            callback_url (str): 由ArkID提供的回调地址
            next_url (str): 前端传来的跳转地址
        Returns:
            str: 第三方登录提供的认证URL
        """
        pass

    def login(self, request, config_id):
        """
        重定向到第三方登录的入口地址, 该入口地址由get_authorize_url提供
        """
        config = self.get_config_by_id(config_id)
        if not config:
            return JsonResponse({"error_msg": "没有找到登录配置"})
        callback_url = config.config.get("callback_url")
        # callback_url = callback_url.replace(
        #     "localhost:8000", "xxxx.vaiwan.com"
        # )  # 内网穿透测试用
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + next_url
        else:
            next_url = ""
        url = self.get_authorize_url(config, callback_url, next_url)

        return HttpResponseRedirect(url)

    @abstractmethod
    def get_ext_token(self, config, code):
        """
        抽象方法
        Args:
            code (str): 第三方认证返回的code
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
        Returns:
            str: 返回第三方认证提供的token
        """
        pass

    @abstractmethod
    def get_ext_user_info(self, config, code, token):
        """
        抽象方法
        Args:
            config (arkid.core.extension.TenantExtensionConfig): 第三方登录的插件运行时配置
            code (str): 第三方认证返回的code
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

    def get_arkid_token(self, ext_id, ext_name, ext_icon, config):
        arkid_user = self.get_arkid_user(ext_id)
        if arkid_user:
            from arkid.core.models import ExpiringToken
            et = ExpiringToken.objects.filter(
                user=arkid_user
            ).first()
            if et and et.expired(config.tenant) is False:
                token = et.token
            else:
                token = refresh_token(arkid_user)
            context = {"token": token}
        else:
            context = {
                "token": "",
                "ext_id": ext_id,
                "ext_name": ext_name,
                "ext_icon": ext_icon,
                "tenant_id": config.tenant.id.hex,
                "bind": config.config.get('bind_url'),
            }

        return context

    @abstractmethod
    def get_auth_code_from_request(self, request):
        """
        抽象方法
        Args:
            request (HTTPRequest): 第三方认证返回的用户标识
        Returns:
            str: 授权码
        """
        pass

    def callback(self, request, config_id):
        """
        拿到请求中携带的code，调用get_ext_token_by_code获取第三方认证的token，
        调用get_user_info_by_ext_token获取第三方认证提供的用户信息，
        拿到ext_id后，判断该ext_id是否已经和ArkID中的用户绑定，如果绑定直接返回绑定用户的Token，
        如果没有，返回重定向到前端绑定页面
        """
        code = self.get_auth_code_from_request(request)
        next_url = request.GET.get("next", '')
        config = self.get_config_by_id(config_id)
        frontend_host = (
            get_app_config()
            .get_frontend_host()
            .replace('http://', '')
            .replace('https://', '')
        )
        # if next_url and (
        #     "third_part_callback" not in next_url or frontend_host not in next_url
        # ):
        #     return JsonResponse({'error_msg': '错误的跳转页面'})
        if next_url and (
            frontend_host not in next_url
        ):
            return JsonResponse({'error_msg': '错误的跳转页面'})
        if code:
            try:
                ext_token = self.get_ext_token(config, code)
                ext_id, ext_name, ext_icon, ext_info = self.get_ext_user_info(
                    config, code, ext_token
                )
            except Exception as e:
                logger.error(e)
                return JsonResponse({"error_msg": "授权码失效", "code": ["invalid"]})
        else:
            return JsonResponse({"error_msg": "授权码丢失", "code": ["required"]})

        context = self.get_arkid_token(ext_id, ext_name, ext_icon, config)
        query_string = urlencode(context)
        if next_url:
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)
        else:
            frontend_host = get_app_config().get_frontend_host()
            frontend_callback = f'{frontend_host}/third_part_callback'
            url = f"{frontend_callback}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

    @abstractmethod
    def bind_arkid_user(self, ext_id, user, data):
        """
        Args:
            ext_id (str): 第三方登录返回的用户标识
            user (arkid.core.models.User): ArkID的用户
            data (dict) request数据
        Returns:
            {"token":xxx}: 返回token
        """
        pass

    @csrf_exempt
    def bind(self, request, config_id):
        """
        处理第三方身份源返回的user_id和ArkID的user之间的绑定
        """
        from urllib.parse import unquote
        from arkid.core.event import SAVE_FILE, dispatch_event, Event
        from arkid.extension.models import Extension

        ext_id = request.POST.get("ext_id")
        user = verify_token(request)
        if not user:
            return JsonResponse({"error_msg": "Token验证失败", "code": ["token invalid"]})
        ext_icon = request.POST.get('ext_icon', '')
        ext_name = request.POST.get('ext_name', '')
        config = self.get_config_by_id(config_id)
        extension = Extension.active_objects.filter(
            type="storage"
        ).first()
        if ext_name:
            ext_name = unquote(ext_name)
            request.POST['ext_name'] = ext_name
        if ext_icon:
            data = {
                'fileurl': ext_icon
            }
            responses = dispatch_event(Event(tag=SAVE_FILE, tenant=config.tenant, request=request, packages=extension.package, data=data))
            useless, (fileinfo, extension) = responses[0]
            request.POST['ext_icon'] = fileinfo
        self.bind_arkid_user(ext_id, user, request.POST)
        # token = refresh_token(user)
        # data = {"token": token}
        data = {}
        return JsonResponse(self.success())

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
            f'api:{self.pname}:{self.pname}_login',
            args=[config_created.id],
        )
        callback_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_callback',
            args=[config_created.id],
        )
        bind_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_bind',
            args=[config_created.id],
        )
        img_url = self.get_img_url()
        config["login_url"] = login_url
        config["callback_url"] = callback_url
        config["bind_url"] = bind_url
        config["img_url"] = img_url
        config_created.config = config
        config_created.save()
        return config_created

    def update_tenant_config(self, id, config, name, type):
        super().update_tenant_config(id, config, name, type)
        config_created = TenantExtensionConfig.valid_objects.filter(id=id).first()
        server_host = get_app_config().get_host()
        login_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_login',
            args=[config_created.id],
        )
        callback_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_callback',
            args=[config_created.id],
        )
        bind_url = server_host + reverse(
            f'api:{self.pname}:{self.pname}_bind',
            args=[config_created.id],
        )
        img_url = self.get_img_url()
        config["login_url"] = login_url
        config["callback_url"] = callback_url
        config["bind_url"] = bind_url
        config["img_url"] = img_url
        config_created.config = config
        config_created.save()
        return config_created

    def add_idp_login_buttons(self, event, **kwargs):
        logger.info(f'{self.package} add idp login buttons start')
        data = {}
        configs = self.get_tenant_configs(event.tenant)
        for config in configs:
            img_url, redirect_url = self.get_img_and_redirect_url(config)
            if img_url and redirect_url:
                buttons = [{"img": img_url, "redirect": {"url": redirect_url}}]
                data[config.id.hex] = {"login": {'extend': {"buttons": buttons}}}

        logger.info(f'{self.package} add idp login buttions end')
        return data
    
    def account_unbind(self, event, **kwargs):
        '''
        在账户解绑的时候会调用此方法，开发者可以根据需要重写此方法
        Params:
            event: 事件参数
                data: 数据
                    user_id: 用户id
        '''
        data = event.data
        pass

    @abstractmethod
    def get_img_and_redirect_url(self, config):
        """
        返回前端渲染第三方登录的按钮
        抽象方法
        Args:
            config (arkid.extension.models.TenantExtensionConfig): 第三方认证提供的Client_ID,

        Returns:
            tuple: 返回图片url和跳转地址('image_url', 'redirect_url')
        """
        pass
