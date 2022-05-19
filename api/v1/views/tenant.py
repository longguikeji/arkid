from typing import List
from ninja import Field, ModelSchema, Query, Schema
from arkid.core.api import api, operation
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema

class TenantListQueryIn(Schema):
    name:str = Field(
        default=None,
    )
        
class TenantListOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id","name", "slug", "icon"]

@api.get("/tenants/", response=List[TenantListOut],tags=["租户管理"],auth=None)
# @operation(List[TenantListOut])
def get_tenant_list(request, query_data:TenantListQueryIn=Query(...)):
    """ 获取租户列表
    """

    tenants = Tenant.active_objects.all()

    return tenants

class TenantOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id","name"]

@api.get("/tenants/{id}/", response=TenantOut,tags=["租户管理"],auth=None)
@operation(TenantOut)
def get_tenant(request, id: str):
    """ 获取租户
    """
    tenant = Tenant.active_objects.get(id=id)
    return tenant

class TenantCreateIn(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["name","slug","icon"]

class TenantCreateOut(Schema):
    pass

@api.post("/tenants/",response=TenantCreateOut,tags=["租户管理"],auth=None)
def create_tenant(request, data:TenantCreateIn):
    """ 创建租户
    """

    tenant = Tenant.valid_objects.create(**data.dict())

    return {}

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
    return {}

class TenantDeleteQueryIn(Schema):
    pass
        
class TenantDeleteOut(Schema):
    pass

@api.delete("/tenants/{id}/", response=TenantDeleteOut, tags=["租户管理"],auth=None)
@operation(TenantDeleteOut)
def delete_tenant(request, id: str, query_data:TenantDeleteQueryIn=Query(...)):
    """ 删除租户
    """
    tenant = Tenant.active_objects.get(id=id)
    tenant.delete()
    return {}


class TenantConfigQueryIn(Schema):
    pass
        
class TenantConfigOut(Schema):
    pass

@api.get("/tenants/{id}/config/", response=TenantConfigOut, tags=["租户管理"],auth=None)
@operation(TenantConfigOut)
def get_tenant_config(request, id: str,query_data:TenantConfigQueryIn=Query(...)):
    """ 获取租户配置,TODO
    """
    return {}

class TenantConfigUpdateQueryIn(Schema):
    pass

class TenantConfigUpdateIn(Schema):
    pass
        
class TenantConfigUpdateOut(Schema):
    pass

@api.post("/tenants/{id}/config/", response=TenantConfigUpdateOut,tags=["租户管理"],auth=None)
@operation(TenantConfigUpdateOut)
def update_tenant_config(request, id: str,data:TenantConfigUpdateIn,query_data:TenantConfigUpdateQueryIn=Query(...)):
    """ 编辑租户配置,TODO
    """
    return {}

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