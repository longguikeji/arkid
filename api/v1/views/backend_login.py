#!/usr/bin/env python3

from tenant.models import Tenant
from common.code import Code
from login_register_config.models import LoginRegisterConfig
from api.v1.serializers.tenant import TenantSerializer
from django.http.response import HttpResponse, JsonResponse
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.template import Template
from django.shortcuts import render
from inventory.models import User
from config import get_app_config
from arkid.settings import LOGIN_URL

@extend_schema(
    tags=['backend-login-api'],
    roles=['general user', 'tenant admin', 'global admin'],
    # responses=PasswordLoginResponseSerializer,
)
class BackendLoginView(APIView):
    """
    此接口主要用于登录ArkId后的第一个调用的接口：
    1，如果是用于OIDC等协议认证，返回单独的登录页面
    2，如果租户打开了kerboros认证，走spnego认证逻辑
    3, 否则跳转到前端登录页面
    """

    def get(self, request):
        tenant = self.get_tenant(request)
        if not tenant:
            tenant = Tenant.active_objects.get(id=1)
        next = request.GET.get('next')
        if not next:
            app_config = get_app_config()
            if tenant.slug:
                front_login = '{}{}'.format(app_config.get_slug_frontend_host(tenant.slug), LOGIN_URL)
            else:
                front_login = '{}{}?tenant={}'.format(app_config.get_frontend_host(), LOGIN_URL, tenant.uuid.hex)
            next = front_login 
        return render(
            request=request,
            template_name="backend_login/backend_login.html",
            context={"tenant_uuid": tenant.uuid.hex, 'next': next},
        )

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.active_objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return JsonResponse(
                {
                    'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                    'message': _('username or password is not correct'),
                }
            )
        token = user.refresh_token()
        return JsonResponse({'token': token.key})


    def get_tenant(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        return tenant

    def get_provider(self, tenant, config_uuid):

        config = LoginRegisterConfig.valid_objects.filter(
            tenant=tenant, uuid=config_uuid
        ).first()
        if not config:
            config_data = {}
        else:
            config_data = config.data

        r = get_app_runtime()
        provider_cls = r.login_register_config_providers.get(config.type)
        if not provider_cls:
            return None

        provider = provider_cls(config_data, tenant=tenant)
        provider.type = config.type
        return provider
