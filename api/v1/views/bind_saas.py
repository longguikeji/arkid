import requests
from arkid.config import get_app_config
from arkid.core.models import Tenant
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.models import Application
from arkid.common.arkstore import create_tenant_oidc_app


class ArkIDBindSaasAPIView(View):

    def post(self, request, tenant_id, *args, **kwargs):
        """
        检查slug是否存在的api
        发送 公司名,联系人,邮箱,手机号,Saas ArkID 租户slug
        本地租户绑定Saas租户
        """
        tenant = Tenant.objects.get(id=tenant_id)

        bind_info = self.get_bind_info(tenant_id)
        if bind_info.get('saas_tenant_slug'):
            bind_info = self.update_saas_binding(tenant, request)
            return JsonResponse(bind_info)
        
        app = self.create_oidc_app()

        try:
            resp = self.create_saas_binding(tenant, request, app)
            if 'error' in resp:
                app.delete()
                return JsonResponse(resp)
        except Exception as e:
            app.delete()
            data = {'error': str(e)}
            return JsonResponse(data)

        app.redirect_uris = resp['callback_url']
        app.save()

        data = {
            'saas_tenant_id': resp['saas_tenant_id'],
            'saas_tenant_slug': resp['saas_tenant_slug'],
        }
        self.create_arkidstore_login_app(tenant, resp['saas_tenant_slug'])
        self.create_arkid_saas_login_app(tenant, resp['saas_tenant_slug'])
        return JsonResponse(data)

    def get(self, request, tenant_id, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        bind_info = self.get_bind_info(tenant_id)
        tenant = Tenant.objects.get(id=tenant_id)
        self.create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
        self.create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
        return JsonResponse(bind_info)

    def patch(self, request, tenant_id, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        tenant = Tenant.objects.get(id=tenant_id)
        bind_info = self.update_saas_binding(tenant, request)
        self.create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
        self.create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
        return JsonResponse(bind_info)

    def get_bind_info(self, tenant_id):
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        params = {'local_tenant_id': tenant_id}
        resp = requests.get(bind_saas_url, params=params)
        if resp.status_code != 200:
            raise Exception(f'Error get_bind_info: {resp.status_code}')
        resp = resp.json()
        return resp

    def create_oidc_app(self):
        redirect_uris = ''
        defaults = {
            'client_type': 'public',
            'redirect_uris': redirect_uris,
            'authorization_grant_type': 'implicit',
            'skip_authorization': True,
            'algorithm': 'RS256',
        }

        app, created = Application.objects.update_or_create(
            name = 'arkid_saas',
            defaults=defaults,
        )
        return app

    def create_saas_binding(self, tenant, request, app):
        data = request.POST
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        host = get_app_config().get_host()
        jwks_url = f"{host}/api/v1/tenant/{tenant.id.hex}/.well-known/jwks.json"
        resp = requests.get(jwks_url)
        if resp.status_code != 200:
            raise Exception(f'Error get_jwks: {resp.status_code}')
        jwks = resp.text
        params = {
            'local_tenant_id': str(tenant.id),
            'local_tenant_slug': tenant.slug,
            'company_name': data['company_name'],
            'contact_person': data['contact_person'],
            'email': data['email'],
            'mobile': data['mobile'],
            'client_id': app.client_id,
            'client_secret': app.client_secret,
            'local_host': host,
            'saas_tenant_slug': data['saas_tenant_slug'],
            'jwks': jwks,
        }
        resp = requests.post(bind_saas_url, json=params)
        if resp.status_code != 200:
            raise Exception(f'Error create_saas_binding: {resp.status_code}')
        resp = resp.json()
        return resp

    def update_saas_binding(self, tenant, request):
        data = request.POST
        bind_saas_url = settings.ARKID_SAAS + '/api/v1/arkid/saas/bind'
        host = get_app_config().get_host()
        params = {
            'local_tenant_id': str(tenant.id),
            'company_name': data['company_name'],
            'contact_person': data['contact_person'],
            'email': data['email'],
            'mobile': data['mobile'],
        }
        resp = requests.patch(bind_saas_url, json=params)
        if resp.status_code != 200:
            raise Exception(f'Error update_saas_binding: {resp.status_code}')
        resp = resp.json()
        return resp

    def create_arkidstore_login_app(self, tenant, saas_tenant_slug):
        url = f"{settings.ARKSTOER_URL}/api/v1/login?tenant_slug={saas_tenant_slug}"
        create_tenant_oidc_app(tenant, url, 'arkstore_login', 'arkidstore login')

    def create_arkid_saas_login_app(self, tenant, saas_tenant_slug):
        arkid_saas_url = settings.ARKID_SAAS
        http, host = arkid_saas_url.split('://', 1)
        url = f"{http}://{saas_tenant_slug}.{host}"
        create_tenant_oidc_app(tenant, url, 'arkdi_saas_login', 'arkid_saas login')


from django.urls import re_path


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_id>[\w-]+)/bind_saas/$',
        ArkIDBindSaasAPIView.as_view(),
        name='bind_saas',
    ),
]