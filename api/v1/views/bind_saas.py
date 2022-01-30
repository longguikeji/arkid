from email.policy import default
import requests
from rest_framework.views import APIView
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from config import get_app_config
from tenant.models import Tenant
# from drf_spectacular.utils import extend_schema
from openapi.utils import extend_schema
from runtime import get_app_runtime
from app.models import App
from common.provider import AppTypeProvider
from django.conf import settings

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ArkIDBindSaasSerializer(serializers.Serializer):

    company_name = serializers.CharField(label=_('公司名'), read_only=False)
    contact_person = serializers.CharField(label=_('联系人'), read_only=False)
    email = serializers.CharField(label=_('邮箱'), read_only=False)
    mobile = serializers.CharField(label=_('手机'), read_only=False)
    local_tenant_slug = serializers.CharField(label=_('本地租户Slug'), read_only=False)
    local_tenant_uuid = serializers.CharField(label=_('本地租户UUID'), read_only=False)
    saas_tenant_slug = serializers.CharField(label=_('中心平台租户Slug'), read_only=False)
    saas_tenant_uuid = serializers.CharField(label=_('中心平台租户UUID'), read_only=False)
    saas_tenant_url = serializers.CharField(label=_('中心平台网址'), read_only=False)


class ArkIDBindSaasCreateSerializer(serializers.Serializer):

    slug = serializers.SlugField(label=_('中心租户Slug'), read_only=False)
    company_name = serializers.CharField(label=_('公司名'), read_only=False)
    contact_person = serializers.CharField(label=_('联系人'), read_only=False)
    email = serializers.EmailField(label=_('邮箱'), read_only=False)
    mobile = serializers.CharField(label=_('手机'), read_only=False)

@extend_schema(tags=["arkid"])
class ArkIDBindSaasAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ArkIDBindSaasSerializer

    @extend_schema(roles=['tenant admin', 'global admin'], responses=ArkIDBindSaasCreateSerializer)
    def post(self, request, tenant_uuid, *args, **kwargs):
        """
        检查slug是否存在的api
        发送 公司名，联系人，邮箱，手机号，Saas ArkID 租户slug
        本地租户绑定Saas租户
        """
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        
        status, app = self.create_oidc_app(tenant)
        if status == 'error':
            data = {'error': '已绑定'}
            return Response(data, HTTP_200_OK)

        try:
            resp = self.create_saas_binding(tenant, request, app)
            if 'error' in resp:
                return Response(resp, HTTP_200_OK)
        except Exception as e:
            app.kill()
            data = {'error': str(e)}
            return Response(data, HTTP_200_OK)
    
        app.data['redirect_uris'] = resp['callback_url']
        app.save()
        
        data = {
            'saas_tenant_uuid': resp['saas_tenant_uuid'],
            'saas_tenant_slug': resp['saas_tenant_slug'],
        }
        return Response(data, HTTP_200_OK)

    @extend_schema(roles=['tenant admin', 'global admin'], request=ArkIDBindSaasSerializer)
    def get(self, request, tenant_uuid, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        params = {'local_tenant_uuid': tenant_uuid}
        resp = requests.get(bind_saas_url, params=params).json()
        return Response(resp, HTTP_200_OK)

    def create_oidc_app(self, tenant):
        url = settings.ARKID_SAAS
        kwargs = {
            'tenant': tenant,
            'name': 'arkid_saas',
            'type': 'OIDC',
        }
        defaults = {
            'url': url,
            'description': '连接中心平台OIDC应用',
            'logo': '',
        }
        app, created = App.active_objects.update_or_create(**kwargs, defaults=defaults)
        if not created:
            return 'error', app

        redirect_uris = ''
        oidc_data = {
            'client_type': 'public',
            'redirect_uris': redirect_uris,
            'grant_type': 'authorization_code',
            'skip_authorization': True,
            'algorithm': 'RS256',
        }
        try:
            r = get_app_runtime()
            provider_cls: AppTypeProvider = r.app_type_providers.get('OIDC', None)
            assert provider_cls is not None
            provider = provider_cls()
            data = provider.create(app=app, data=oidc_data)
            if data is not None:
                app.data = data
                app.save()
        except Exception as e:
            app.kill()
            raise Exception(e)
        
        return 'ok', app

    def create_saas_binding(self, tenant, request, app):
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        host = get_app_config().get_frontend_host()
        params = {
            'local_tenant_uuid': tenant.uuid,
            'local_tenant_slug': tenant.slug,
            'company_name': request.data['company_name'],
            'contact_person': request.data['contact_person'],
            'email': request.data['email'],
            'mobile': request.data['mobile'],
            'client_id': app.data['client_id'],
            'client_secret': app.data['client_secret'],
            'local_host': host,
            'saas_tenant_slug': request.data['saas_tenant_slug'],
        }
        resp = requests.post(bind_saas_url, json=params).json()
        return resp