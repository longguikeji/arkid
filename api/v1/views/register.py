#!/usr/bin/env python3

from tenant.models import Tenant, TenantConfig
from system.models import SystemConfig
from common.code import Code
from login_register_config.models import LoginRegisterConfig
from api.v1.serializers.tenant import TenantSerializer
from django.http.response import JsonResponse
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.views import APIView
from common.utils import (
    check_password_complexity,
    get_request_tenant,
    get_client_ip,
    set_user_register_count,
    get_user_register_count,
)
from django.utils.translation import gettext_lazy as _


@extend_schema(
    tags=['register-api'],
    roles=['general user', 'tenant admin', 'global admin'],
    # responses=PasswordLoginResponseSerializer,
)
class RegisterView(APIView):
    def post(self, request):
        tenant = get_request_tenant(request)

        config = self.get_system_or_tenant_config(tenant)
        is_open_register_limit = config.data.get('is_open_register_limit', False)
        register_time_limit = config.data.get('register_time_limit', 1)
        register_count_limit = config.data.get('register_count_limit', 10)

        ip = get_client_ip(request)
        if is_open_register_limit:
            register_count = get_user_register_count(ip)
            if register_count >= register_count_limit:
                return JsonResponse(
                    data={
                        'error': Code.REGISTER_FAST_ERROR.value,
                        'message': _('a large number of registrations in a short time'),
                    }
                )

        extention_type = request.data.get('extension', None)

        if not extention_type:
            return {
                'error': Code.POST_DATA_ERROR.value,
                'message': 'No extention in post data',
            }

        provider = self.get_provider(tenant, extention_type)
        if not provider:
            return {
                'error': Code.PROVIDER_NOT_EXISTS_ERROR.value,
                'message': f'No provider: {extention_type} found',
            }

        # 获取登录注册配置
        ret = provider.register_user(request)
        if ret.get('error') != Code.OK.value:
            return JsonResponse(ret)

        user = ret.get('user')

        if not tenant:
            user.is_platform_user = True
        else:
            user.tenants.add(tenant)
        user.save()

        token = user.refresh_token()
        return_data = {'token': token.key, 'user_uuid': user.uuid.hex}

        if is_open_register_limit:
            set_user_register_count(ip, 'register', register_time_limit)

        return JsonResponse(data={'error': Code.OK.value, 'data': return_data})

    def get_provider(self, tenant, extention_type):

        r = get_app_runtime()
        provider_cls = r.login_register_config_providers.get(extention_type)
        if not provider_cls:
            return None
        config = LoginRegisterConfig.valid_objects.filter(
            tenant=tenant, type=extention_type
        ).first()
        if not config:
            config_data = {}

        else:
            config_data = config.data

        provider = provider_cls(config_data)
        return provider

    def get_system_or_tenant_config(self, tenant):
        config = None
        if tenant:
            config = TenantConfig.valid_objects.filter(tenant=tenant).first()
        else:
            config = SystemConfig.valid_objects.filter().first()

        return config
