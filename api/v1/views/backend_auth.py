#!/usr/bin/env python3

from django.http import response
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
from backend_login.models import BackendLogin
import logging
logger = logging.getLogger(__name__)

@extend_schema(
    tags=['backend-auth-api'],
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    # responses=PasswordLoginResponseSerializer,
)
class BackendAuthView(APIView):
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
        backend_login_providers = get_app_runtime().backend_login_providers
        backend_login_configs = BackendLogin.valid_objects.filter(tenant=tenant).order_by('order_no')
        if not backend_login_configs:
            return JsonResponse({'token': ''})
        backend_login_providers = get_app_runtime().backend_login_providers
        if not backend_login_providers:
            return JsonResponse({'token': ''})
        for config in backend_login_configs:
            provider_cls = backend_login_providers.get(config.type) 
            if not provider_cls:
                continue
            try:
                user, response = provider_cls().authenticate(tenant, request, config.data)
            except Exception as e:
                logger.exception(e)
                continue
            if response:
                return response
            elif user:
                token = user.refresh_token()
                return JsonResponse({'token': token.key})
            else:
                continue 
        return JsonResponse({'token': ''})


    def get_tenant(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        return tenant