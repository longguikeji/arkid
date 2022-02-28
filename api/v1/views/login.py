#!/usr/bin/env python3
from tenant.models import Tenant
from common.code import Code
from login_register_config.models import LoginRegisterConfig
from api.v1.serializers.tenant import TenantSerializer
from django.http.response import JsonResponse
from runtime import get_app_runtime
from openapi.utils import extend_schema
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from inventory.models import Permission, PermissionGroup
from tasks.tasks import update_permission

from config import get_app_config


import requests
import json
import uuid


@extend_schema(
    tags=['login-api'],
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    summary='登录'
    # responses=PasswordLoginResponseSerializer,
)
class LoginView(APIView):
    def post(self, request):
        tenant = self.get_tenant(request)

        config_uuid = request.data.get('config_uuid', None)
        if not config_uuid:
            return {
                'error': Code.POST_DATA_ERROR.value,
                'message': 'No config uuid in post data',
            }

        provider = self.get_provider(tenant, config_uuid)
        if not provider:
            return {
                'error': Code.PROVIDER_NOT_EXISTS_ERROR.value,
                'message': f'No provider found',
            }

        # 获取登录注册配置
        ret = provider.authenticate(request)
        r = get_app_runtime()

        if ret.get('error') != Code.OK.value:

            # 失败后调用认证规则
            for rule in r.auth_rules:
                ret = rule.provider.authenticate_failed(rule, request, ret, tenant, provider.type)
            return JsonResponse(ret)

        else:
            user = ret.get('user')
            
        if tenant and not user.is_superuser:
            if tenant not in user.tenants.all():
                return JsonResponse(
                    data = {
                    'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                    'message': _('username or password is not correct'),
                })
              
        for rule in r.auth_rules:
            ret = rule.provider.authenticate_success(rule, request, ret, user, tenant, provider.type)

        token = user.refresh_token()
        return_data = {'token': token.key, 'user_uuid': user.uuid.hex}
        if tenant:
            return_data['has_tenant_admin_perm'] = tenant.has_admin_perm(user)
        else:
            return_data['tenants'] = [
                TenantSerializer(o).data for o in user.tenants.all()
            ]
        # 需要在此处插入api格式缓存权限数据
        update_permission.delay()
        return JsonResponse(data={'error': Code.OK.value, 'data': return_data})

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
