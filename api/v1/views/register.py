#!/usr/bin/env python3

from tenant.models import Tenant
from common.code import Code
from login_register_config.models import LoginRegisterConfig
from api.v1.serializers.tenant import TenantSerializer
from django.http.response import JsonResponse
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.views import APIView
from common.utils import check_password_complexity


@extend_schema(
    tags=['register-api'],
    roles=['general user', 'tenant admin', 'global admin'],
    # responses=PasswordLoginResponseSerializer,
)
class RegisterView(APIView):
    def post(self, request):
        tenant = self.get_tenant(request)
        # TODO password complexity check
        if 'password' in request.data:
            ret, message = check_password_complexity(
                request.data.get('password'), tenant
            )
            if not ret:
                return JsonResponse(
                    data={
                        'error': Code.PASSWORD_STRENGTH_ERROR.value,
                        'message': message,
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

        return JsonResponse(data={'error': Code.OK.value, 'data': return_data})

    def get_tenant(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        return tenant

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
