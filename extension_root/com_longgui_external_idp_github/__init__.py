from django.urls import reverse
from arkid.config import get_app_config
from arkid.core.extension.external_idp import ExternalIdpExtension
from .github_schema import (
    GithubConfigSchema,
)
from oauth2_provider.models import Application
from oauth2_provider.urls import urlpatterns as urls
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .constants import AUTHORIZE_URL, IMG_URL
from urllib.parse import urlencode, unquote
import urllib.parse
from .user_info_manager import GithubUserInfoManager, APICallError
from .models import GithubUser
from arkid.core.token import refresh_token
from arkid.core.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


package = 'com.longgui.external_idp.github'

GithubConfigSchema = create_extension_schema(
    'GithubConfigSchema', package, base_schema=GithubConfigSchema
)


class ExternalIdpGithubExtension(ExternalIdpExtension):
    def load(self):
        # 加载url地址
        # self.load_urls()
        # 加载相应的配置文件
        super().load()
        self.register_extend_field(GithubUser, "github_user_id")
        self.register_external_idp_schema(self.type, GithubConfigSchema)

    def get_img_url(self):
        return IMG_URL

    def login(self, request, tenant_id, settings_id):
        c = get_app_config()
        # @TODO: keep other query params
        tenant_settings = TenantExtension.valid_objects.filter(id=settings_id).first()
        if not tenant_settings:
            return JsonResponse({"error_msg": "没有找到Github登录配置"})
        settings = tenant_settings.settings
        callback_url = settings.get("callback_url")
        client_id = settings.get("client_id")
        next_url = request.GET.get("next", None)
        if next_url is not None:
            next_url = "?next=" + next_url
        else:
            next_url = ""
        redirect_uri = "{}{}".format(callback_url, next_url)
        url = "{}?client_id={}&redirect_uri={}".format(
            AUTHORIZE_URL,
            client_id,
            redirect_uri,
        )
        return HttpResponseRedirect(url)

    def callback(self, request, tenant_id, settings_id):
        """
        处理github用户登录之后重定向页面
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
                tenant_settings = TenantExtension.valid_objects.filter(
                    id=settings_id
                ).first()
                settings = tenant_settings.settings
                client_id = settings.get("client_id")
                client_secret = settings.get("client_secret")
                user_id = GithubUserInfoManager(client_id, client_secret).get_user_id(
                    code
                )
            except APICallError:
                return JsonResponse({"error_msg": "授权码失效", "code": ["invalid"]})
        else:
            return JsonResponse({"error_msg": "授权码丢失", "code": ["required"]})

        context = self.get_token(user_id, tenant_id, settings_id)
        if next_url:
            query_string = urlencode(context)
            url = f"{next_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)
        return JsonResponse(context)

    def get_token(self, user_id, tenant_id, settings_id):
        github_user = GithubUser.valid_objects.filter(github_user_id=user_id).first()
        tenant_settings = TenantExtension.valid_objects.filter(id=settings_id).first()
        if github_user:
            user = github_user.user
            token = refresh_token(user)
            context = {"token": token}
        else:
            context = {
                "token": "",
                "user_id": user_id,
                "tenant_id": tenant_id,
                "bind": tenant_settings.settings.get('callback_url'),
            }

        return context

    @csrf_exempt
    def bind(self, request, tenant_id, settings_id):
        """
        绑定用户
        """
        user_id = request.POST.get("user_id")
        user = User.valid_objects.filter().first()
        user.github_user_id = user_id
        user.save()
        token = refresh_token(user)
        data = {"token": token}
        return JsonResponse(data)


extension = ExternalIdpGithubExtension(
    package=package,
    description='Github第三方登录服务',
    version='1.0',
    labels='external-idp-github',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
