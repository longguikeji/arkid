#!/usr/bin/env python3

from tenant.models import Tenant
from common.code import Code
from login_register_config.models import LoginRegisterConfig
from api.v1.serializers.tenant import TenantSerializer
from django.http.response import JsonResponse
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.views import APIView


@extend_schema(
    tags=['reset-password-api'],
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    # responses=PasswordLoginResponseSerializer,
)
class ResetPWDView(APIView):
    def post(self, request):
        tenant = self.get_tenant(request)
        # TODO password complexity check
        config_uuid = request.data.get('config_uuid', None)
        if not config_uuid:
            return {
                'error': Code.POST_DATA_ERROR.value,
                'message': 'No extention in post data',
            }

        provider = self.get_provider(tenant, config_uuid)
        if not provider:
            return {
                'error': Code.PROVIDER_NOT_EXISTS_ERROR.value,
                'message': f'No provider found',
            }

        # 获取登录注册配置
        ret = provider.reset_password(request)
        if ret.get('error') != Code.OK.value:
            return JsonResponse(ret)

        return JsonResponse(
            {'error': Code.OK.value, 'message': 'Reset password success'}
        )

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

        provider = provider_cls(config_data)
        return provider
