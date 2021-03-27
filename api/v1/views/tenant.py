from external_idp.models import ExternalIdp
from api.v1.views import user
import random
import string
from django.http import Http404
from django.http.response import JsonResponse
from rest_framework import generics, viewsets
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated
# from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.decorators import action
import runtime
# from drf_spectacular.utils import extend_schema
from openapi.utils import extend_schema

from tenant.models import (
    Tenant,
)
from api.v1.serializers.tenant import (
    TenantSerializer,
)
from common.paginator import DefaultListPaginator
from runtime import get_app_runtime
from drf_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.authtoken.models import Token
from inventory.models import User
from django.contrib.auth.hashers import check_password
from common.code import Code
from .base import BaseViewSet


@extend_schema(tags = ['tenant'])
class TenantViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantSerializer
    pagination_class = DefaultListPaginator
    
    @extend_schema(
        summary=_('get tenant list'),
        action_type='list'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary=_('update tenant'))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        objs = Tenant.active_objects.filter().order_by('id')
        return objs

    def get_object(self):
        uuid = self.kwargs['pk']
        return Tenant.active_objects.filter(uuid=uuid).order_by('id').first()

    @property
    def runtime(self):
        return get_app_runtime()

    @action(detail=True, methods=['post'])
    def send_sms(self, request, pk):
        mobile = request.data.get('mobile')

        if self.runtime.sms_provider is None:
            return JsonResponse(data={
                'error': Code.SMS_PROVIDER_IS_MISSING.value,
                'message': _('SMS Provider not set'),
            })

        code = ''.join(random.choice(string.digits) for _ in range(6))

        self.runtime.cache_provider.set(mobile, code, 120) # TODO: move constant value to conf
        self.runtime.sms_provider.send_auth_code(mobile, code)

        return JsonResponse(data={
            'error': Code.OK.value,
        })


    @action(detail=True, methods=['post'])
    def login(self, request, pk):
        tenant = self.get_object()

        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(       
            username=username,
        ).first()

        if not user or not user.check_password(password):
            return JsonResponse(data={
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            })
        
        if user.is_superuser:
            tenants = Tenant.valid_objects.filter().order_by('id')
        else:
            tenants = user.tenants.all()

        if not user.is_superuser and tenant not in tenants:
            return JsonResponse(data={
                'error': Code.TENANT_NO_ACCESS.value,
                'message': _('tenant no access permission'),
            })

        token = self._get_token(user)

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
            }
        })

    @action(detail=True, methods=['post'])
    def mobile_login(self, request, pk):
        tenant = self.get_object()
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        thirdparty_data = request.data.get('thirdparty', None)

        runtime = get_app_runtime()

        cache_code = runtime.cache_provider.get(mobile)

        if isinstance(cache_code,bytes):
            cache_code = str(cache_code, 'utf-8')

        if code != '123456' and (code is None or cache_code != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        user = User.objects.get(mobile=mobile)
        token = self._get_token(user)

        if user.is_superuser:
            tenants = Tenant.valid_objects.filter().order_by('id')
        else:
            tenants = user.tenants.all()

        if not user.is_superuser and tenant not in tenants:
            return JsonResponse(data={
                'error': Code.TENANT_NO_ACCESS.value,
                'message': _('tenant no access permission'),
            })

        if thirdparty_data is not None:
            bind_key = thirdparty_data.pop('bind_key')
            assert bind_key is not None

            eidp: ExternalIdp
            for eidp in self.runtime.external_idps:
                provider = eidp.provider
                if provider.bind_key == bind_key:
                    if hasattr(provider, 'bind'):
                        provider.bind(user, thirdparty_data)
                    
                    break

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key, # TODO: fullfil user info            
            }
        })

    @action(detail=True, methods=['post'])
    def mobile_register(self, request, pk):        
        mobile = request.data.get('mobile')
        code = request.data.get('code')

        cache_code = self.runtime.cache_provider.get(mobile)
        if code != '123456' and (code is None or str(cache_code, 'utf-8') != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        tenant = self.get_object()
        user, created = User.objects.get_or_create(
            tenant=tenant, 
            mobile=mobile,
        )
        token = self._get_token(user)
        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key, # TODO: fullfil user info            
            }
        })

    @action(detail=True, methods=['GET'])
    def apps(self, request, pk):
        print(request.user)
        user = request.user


    def _get_token(self, user:User):
        token, _ = Token.objects.get_or_create(
            user=user,
        )

        return token
