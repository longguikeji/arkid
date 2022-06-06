from arkid.core.models import Tenant
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from arkid.common.bind_saas import (
    get_bind_info,
    update_saas_binding,
    set_saas_bind_slug,
    create_arkidstore_login_app,
    create_arkid_saas_login_app,
    bind_saas,
)
from ninja import Schema
from pydantic import Field
from typing import Optional
from arkid.core.api import api


class BindSaasSchemaOut(Schema):
    company_name: Optional[str] = Field(readonly=True)
    contact_person: Optional[str] = Field(readonly=True)
    email: Optional[str] = Field(readonly=True, default='')
    mobile: Optional[str] = Field(readonly=True)
    # local_tenant_id: str = Field(hidden=True)
    # local_tenant_slug: str = Field(hidden=True)
    saas_tenant_id: str = Field(readonly=True)
    saas_tenant_slug: Optional[str]  = Field(readonly=True, default='')
    # saas_tenant_url: str = Field(hidden=True)


class BindSaasSlugSchemaOut(Schema):
    saas_tenant_slug: Optional[str]


class BindSaasInfoSchema(Schema):
    company_name: Optional[str]
    contact_person: Optional[str]
    email: Optional[str]
    mobile: Optional[str]


@api.get("/tenant/{tenant_id}/bind_saas/", tags=['中心平台'], response=BindSaasSchemaOut)
def get_bind_saas(request, tenant_id: str):
    """
    查询 saas 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    if not bind_info.get('saas_tenant_id'):
        bind_info = bind_saas(tenant_id)
    return bind_info


@api.get("/tenant/{tenant_id}/bind_saas/slug/", tags=['中心平台'], response=BindSaasSlugSchemaOut)
def get_bind_saas_slug(request, tenant_id: str):
    """
    查询 saas slug 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/slug/", tags=['中心平台'])
def set_bind_saas_slug(request, tenant_id: str, data: BindSaasSlugSchemaOut):
    """
    设置 saas slug 绑定信息
    """
    tenant = Tenant.objects.get(id=tenant_id)
    bind_info = set_saas_bind_slug(tenant, data.dict())
    create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
    create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
    return bind_info


@api.get("/tenant/{tenant_id}/bind_saas/info/", tags=['中心平台'], response=BindSaasInfoSchema)
def get_bind_saas_info(request, tenant_id: str):
    """
    查询 saas info 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/info/", tags=['中心平台'])
def update_bind_saas_info(request, tenant_id: str, data: BindSaasInfoSchema):
    """
    更新 saas info 绑定信息
    """
    tenant = Tenant.objects.get(id=tenant_id)
    bind_info = update_saas_binding(tenant, data.dict())
    create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
    create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/", tags=['中心平台'])
def create_bind_saas(request, tenant_id: str):
    """
    检查slug是否存在的api
    发送 公司名,联系人,邮箱,手机号,Saas ArkID 租户slug
    本地租户绑定Saas租户
    """
    data = bind_saas(tenant_id, request.POST)
    return data

