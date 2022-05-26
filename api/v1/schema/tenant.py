from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.models import Tenant
from arkid.core.schema import ResponseSchema


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
    
class TenantItemOut(ModelSchema):

    class Config:
        model = Tenant
        model_fields = ["name","slug","icon"]
        
class TenantOut(ResponseSchema):
    
    data: TenantItemOut
    
class TenantCreateIn(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["name","slug","icon"]

class TenantCreateOut(ResponseSchema):
    pass

class TenantUpdateIn(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["name"]
        
class TenantUpdateOut(Schema):
    pass

class TenantDeleteOut(ResponseSchema):
    pass

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

class DefaultTenantItemOut(ModelSchema):
    
    class Config:
        model = Tenant
        model_fields = ["id", "name"]

class DefaultTenantOut(ResponseSchema):
    data: DefaultTenantItemOut