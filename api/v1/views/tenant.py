from re import T
from typing import List
from uuid import UUID
from ninja import Field, File, ModelSchema, Query, Schema
from arkid.core.api import api, operation
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.error import ErrorCode

class TenantListQueryIn(Schema):
    name__contains:str = Field(
        default="",
        title=_("租户名称")
    )
        
class TenantListItemOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id","name", "slug", "icon"]
        
class TenantListOut(ResponseSchema):
    data: List[TenantListItemOut]

@api.get("/tenants/", response=TenantListOut,tags=["租户管理"],auth=None)
# @operation(List[TenantListOut])
def get_tenant_list(request, query_data:TenantListQueryIn=Query(...)):
    """ 获取租户列表
    """

    tenants = Tenant.active_objects
    query_data = query_data.dict()
    if query_data:
        tenants = tenants.filter(**query_data)

    return {
        "data": list(tenants.all())
    }

class TenantItemOut(ModelSchema):

    class Config:
        model = Tenant
        model_fields = ["name","slug","icon"]
        
class TenantOut(ResponseSchema):
    
    data: TenantItemOut

@api.get("/tenants/{id}/", response=TenantOut,tags=["租户管理"],auth=None)
@operation(TenantOut)
def get_tenant(request, id: str):
    """ 获取租户
    """
    tenant = Tenant.active_objects.get(id=id)
    return {
        "data": {
            "name":tenant.name,
            "slug": tenant.slug,
            "icon": tenant.icon        
        }
    }

class TenantCreateIn(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["name","slug","icon"]

class TenantCreateOut(ResponseSchema):
    pass

@api.post("/tenants/",response=TenantCreateOut,tags=["租户管理"],auth=None)
def create_tenant(request, data:TenantCreateIn):
    """ 创建租户
    """

    tenant = Tenant.valid_objects.create(**data.dict())
    return {'error': ErrorCode.OK.value}
class TenantUpdateIn(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["name"]
        
class TenantUpdateOut(Schema):
    pass

@api.post("/tenants/{id}/", response=TenantUpdateOut,tags=["租户管理"],auth=None)
@operation(TenantUpdateOut)
def update_tenant(request, id: str, data:TenantUpdateIn):
    """ 编辑租户
    """
    tenant = Tenant.active_objects.get(id=id)
    tenant.name = data.dict().get("name")
    tenant.save()
    return {'error': ErrorCode.OK.value}


class TenantDeleteOut(ResponseSchema):
    pass

@api.delete("/tenants/{id}/", response=TenantDeleteOut, tags=["租户管理"],auth=None)
@operation(TenantDeleteOut)
def delete_tenant(request, id: str):
    """ 删除租户
    """
    tenant = Tenant.active_objects.get(id=id)
    tenant.delete()
    return {'error': ErrorCode.OK.value}
        
class TenantConfigItemOut(Schema):
    id: str = Field(
        readonly = True
    )
    
    name: str = Field(
        title=_("租户名称"),
    )
    
    slug: str = Field(
        title=_("slug")
    )
    
    icon: str = Field(
        title=_("图标")
    )

class TenantConfigOut(ResponseSchema):
    data: TenantConfigItemOut

@api.get("/tenants/{tenant_id}/config/", response=TenantConfigOut, tags=["租户管理"],auth=None)
@operation(TenantConfigOut)
def get_tenant_config(request, tenant_id: str):
    """ 获取租户配置
    """
    tenant = request.tenant
    
    return {
        "data": {
            "id": tenant.id.hex,
            "name": tenant.name,
            "slug": tenant.slug,
            "icon": tenant.icon
        }
    }


class TenantConfigUpdateIn(Schema):
    name: str = Field(
        title=_("租户名称"),
    )
    
    slug: str = Field(
        title=_("slug")
    )
    
    icon: str = Field(
        title=_("图标")
    )
        
class TenantConfigUpdateOut(ResponseSchema):
    pass

@api.post("/tenants/{tenant_id}/config/", response=TenantConfigUpdateOut,tags=["租户管理"],auth=None)
@operation(TenantConfigUpdateOut)
def update_tenant_config(request, tenant_id: str,data:TenantConfigUpdateIn):
    """ 编辑租户配置,TODO
    """
    return {'error': ErrorCode.OK.value}

class DefaultTenantItemOut(ModelSchema):
    
    class Config:
        model = Tenant
        model_fields = ["id", "name"]

class DefaultTenantOut(ResponseSchema):
    data: DefaultTenantItemOut

@api.get("/default_tenant/",response=DefaultTenantOut, tags=["租户管理"], auth=None)
def default_tenant(request):
    """ 获取当前域名下的默认租户(如无slug则为平台租户)
    """
    tenant = Tenant.active_objects.order_by("id").first()
    return {"data":tenant}