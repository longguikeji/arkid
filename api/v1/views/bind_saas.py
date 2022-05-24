from arkid.core.models import Tenant
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from arkid.common.bind_saas import (
    create_oidc_app,
    get_bind_info,
    update_saas_binding,
    create_saas_binding,
    create_arkidstore_login_app,
    create_arkid_saas_login_app,
    bind_saas,
)


class ArkIDBindSaasAPIView(View):

    @csrf_exempt
    def post(self, request, tenant_id, *args, **kwargs):
        """
        检查slug是否存在的api
        发送 公司名,联系人,邮箱,手机号,Saas ArkID 租户slug
        本地租户绑定Saas租户
        """
        tenant = Tenant.objects.get(id=tenant_id)
        data = bind_saas(request.POST)
        return JsonResponse(data)

    def get(self, request, tenant_id, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        bind_info = get_bind_info(tenant_id)
        tenant = Tenant.objects.get(id=tenant_id)
        create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
        create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
        return JsonResponse(bind_info)

    @csrf_exempt
    def patch(self, request, tenant_id, *args, **kwarg):
        """
        查询 saas 绑定信息
        """
        tenant = Tenant.objects.get(id=tenant_id)
        bind_info = update_saas_binding(tenant, request.POST)
        create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
        create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
        return JsonResponse(bind_info)


from django.urls import re_path


urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_id>[\w-]+)/bind_saas/$',
        ArkIDBindSaasAPIView.as_view(),
        name='bind_saas',
    ),
]