from re import T
from typing import List
from uuid import UUID
from django.shortcuts import get_object_or_404
from ninja import Field, File, ModelSchema, Query, Schema
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.error import ErrorCode, ErrorDict
from api.v1.schema.tenant import *
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.event import(
    CREATE_TENANT, Event, register_event,
    dispatch_event
)



@api.get("/tenants/", response=List[TenantListItemOut],tags=["租户管理"])
@operation(List[TenantListItemOut], roles=[PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_tenant_list(request, query_data:TenantListQueryIn=Query(...)):
    """ 获取租户列表
    """

    tenants = Tenant.expand_objects
    query_data = query_data.dict()
    if query_data:
        tenants = tenants.filter(**query_data)

    return tenants

@api.get("/tenants/{id}/", response=TenantOut,tags=["租户管理"], auth=None)
@operation(TenantOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_tenant(request, id: str):
    """ 获取租户
    """
    tenant = Tenant.expand_objects.get(id=id)
    return {
        "data": tenant
    }

@api.post("/tenants/",response=TenantCreateOut,tags=["租户管理"])
@operation(TenantOut,roles=[NORMAL_USER, PLATFORM_USER, PLATFORM_ADMIN])
def create_tenant(request, data:TenantCreateIn):
    """ 创建租户
    """
    user = request.user
    tenant = Tenant.expand_objects.create(**data.dict())
    tenant.users.add(user)
    # 分发一个创建租户的事件
    dispatch_event(Event(tag=CREATE_TENANT, tenant=tenant, request=request, data=user))
    return ErrorDict(ErrorCode.OK)

@api.post("/tenants/{id}/", response=TenantUpdateOut,tags=["租户管理"])
@operation(TenantUpdateOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_tenant(request, id: str, data:TenantUpdateIn):
    """ 编辑租户
    """
    tenant = get_object_or_404(Tenant.expand_objects,id=id)
    for attr, value in data.dict().items():
        setattr(tenant, attr, value)
    tenant.save()
    return ErrorDict(ErrorCode.OK)

@api.delete("/tenants/{id}/", response=TenantDeleteOut, tags=["租户管理"])
@operation(TenantDeleteOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_tenant(request, id: str):
    """ 删除租户
    """
    tenant = Tenant.active_objects.get(id=id)
    tenant.delete()
    return ErrorDict(ErrorCode.OK)

@api.get("/tenants/{tenant_id}/config/", response=TenantConfigOut, tags=["租户管理"])
@operation(TenantConfigOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_tenant_config(request, tenant_id: str):
    """ 获取租户配置
    """
    tenant = get_object_or_404(Tenant.expand_objects,id=tenant_id)
    
    return {
        "data": tenant
    }

@api.post("/tenants/{tenant_id}/config/", response=TenantConfigUpdateOut,tags=["租户管理"])
@operation(TenantConfigUpdateOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_tenant_config(request, tenant_id: str,data:TenantConfigUpdateIn):
    """ 编辑租户配置
    """
    tenant = get_object_or_404(Tenant.expand_objects,id=tenant_id)
    for attr, value in data.dict().items():
        setattr(tenant, attr, value)
    tenant.save()
    return ErrorDict(ErrorCode.OK)

@api.get("/default_tenant/",response=DefaultTenantOut, tags=["租户管理"], auth=None)
def default_tenant(request):
    """ 获取当前域名下的默认租户(如无slug则为平台租户)
    """
    tenant = Tenant.platform_tenant()
    return {"data":tenant}