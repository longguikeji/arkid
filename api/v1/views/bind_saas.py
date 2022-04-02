import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from config import get_app_config
from tenant.models import Tenant
# from drf_spectacular.utils import extend_schema
from openapi.utils import extend_schema
from runtime import get_app_runtime
from app.models import App
from common.provider import AppTypeProvider
from django.conf import settings
from perm.custom_access import ApiAccessPermission
from oauth2_provider.models import Application
from api.v1.serializers.bind_saas import ArkIDBindSaasSerializer, ArkIDBindSaasCreateSerializer


@extend_schema(tags=["arkid"])
class ArkIDBindSaasAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ArkIDBindSaasSerializer

    @extend_schema(roles=['globaladmin'], responses=ArkIDBindSaasCreateSerializer, summary='本地租户绑定Saas租户')
    def post(self, request, tenant_uuid, *args, **kwargs):
        """
        检查slug是否存在的api
        发送 公司名,联系人,邮箱,手机号,Saas ArkID 租户slug
        本地租户绑定Saas租户
        """
        tenant = Tenant.objects.get(uuid=tenant_uuid)

        bind_info = self.get_bind_info(tenant_uuid)
        if bind_info.get('saas_tenant_slug'):
            bind_info = self.update_saas_binding(tenant, request)
            return Response(bind_info, HTTP_200_OK)
        
        app = self.create_oidc_app()

        try:
            resp = self.create_saas_binding(tenant, request, app)
            if 'error' in resp:
                app.kill()
                return Response(resp, HTTP_200_OK)
        except Exception as e:
            app.kill()
            data = {'error': str(e)}
            return Response(data, HTTP_200_OK)

        app.redirect_uris = resp['callback_url']
        app.save()

        data = {
            'saas_tenant_uuid': resp['saas_tenant_uuid'],
            'saas_tenant_slug': resp['saas_tenant_slug'],
        }
        return Response(data, HTTP_200_OK)

    @extend_schema(roles=['globaladmin'], request=ArkIDBindSaasSerializer, summary='查询saas绑定信息')
    def get(self, request, tenant_uuid, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        bind_info = self.get_bind_info(tenant_uuid)
        return Response(bind_info, HTTP_200_OK)

    @extend_schema(roles=['tenant admin', 'global admin'], request=ArkIDBindSaasSerializer)
    def patch(self, request, tenant_uuid, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        bind_info = self.update_saas_binding(tenant, request)
        return Response(bind_info, HTTP_200_OK)

    def get_bind_info(self, tenant_uuid):
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        params = {'local_tenant_uuid': tenant_uuid}
        resp = requests.get(bind_saas_url, params=params).json()
        return resp

    def create_oidc_app(self):
        redirect_uris = ''
        defaults = {
            'client_type': 'public',
            'redirect_uris': redirect_uris,
            'authorization_grant_type': 'authorization-code',
            'skip_authorization': True,
            'algorithm': 'RS256',
        }

        app, created = Application.objects.update_or_create(
            name = 'arkid_saas',
            defaults=defaults,
        )
        return app

    def create_saas_binding(self, tenant, request, app):
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        host = get_app_config().get_host()
        params = {
            'local_tenant_uuid': str(tenant.uuid),
            'local_tenant_slug': tenant.slug,
            'company_name': request.data['company_name'],
            'contact_person': request.data['contact_person'],
            'email': request.data['email'],
            'mobile': request.data['mobile'],
            'client_id': app.client_id,
            'client_secret': app.client_secret,
            'local_host': host,
            'saas_tenant_slug': request.data['saas_tenant_slug'],
        }
        resp = requests.post(bind_saas_url, json=params).json()
        return resp

    def update_saas_binding(self, tenant, request):
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        host = get_app_config().get_host()
        params = {
            'local_tenant_uuid': str(tenant.uuid),
            'company_name': request.data['company_name'],
            'contact_person': request.data['contact_person'],
            'email': request.data['email'],
            'mobile': request.data['mobile'],
        }
        resp = requests.patch(bind_saas_url, json=params).json()
        return resp

    def create_arkidstore_login_app(self, tenant, saas_tenant_slug):
        # url = f"{settings.ARKSTOER_URL.rstrip('/')}/api/v1/login?tenant_slug={resp['saas_tenant_slug']}"
        pass

    def create_arkid_saas_login_app(self, tenant, saas_tenant_slug):
        # url = settings.ARKID_SAAS
        pass
