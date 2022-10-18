from typing import List, Optional
from uuid import UUID
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
    items: List[TenantListItemOut]
    
class TenantItemOut(ModelSchema):

    class Config:
        model = Tenant
        model_fields = ["id","name","slug","icon"]
        
    is_platform_tenant:bool = Field(
        title=_("是否是平台租户")
    )
    
    @staticmethod
    def resolve_is_platform_tenant(obj):
        return obj.is_platform_tenant
        
class TenantOut(ResponseSchema):
    
    data: TenantItemOut
    
class TenantCreateIn(ModelSchema):

    slug:str = Field(
        title=_("短链接标识"),
        format="^[a-z0-9]{1,24}$",
        feedback=_("输入错误，必须为24位以内数字和小写字母的组合")
    )

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
    id: UUID = Field(
        readonly = True
    )
    
    name: str = Field(
        title=_("租户名称"),
    )
    
    slug: Optional[str] = Field(
        title=_("slug")
    )
    
    icon: Optional[str] = Field(
        title=_("图标")
    )
    
    token_duration_minutes: int = Field(
        title=_('Token有效时长(分钟)')
    )

class TenantConfigOut(ResponseSchema):
    data: TenantConfigItemOut
    
class TenantConfigUpdateIn(Schema):
    name: str = Field(
        title=_("租户名称"),
    )
    
    slug: Optional[str] = Field(
        title=_("slug")
    )
    
    icon: Optional[str] = Field(
        title=_("图标")
    )
    
    token_duration_minutes: Optional[int] = Field(
        title=_('Token有效时长(分钟)')
    )
    
class TenantConfigUpdateOut(ResponseSchema):
    pass

class DefaultTenantItemOut(ModelSchema):
    
    class Config:
        model = Tenant
        model_fields = ["id", "name", "icon", "slug"]
        
    is_platform_tenant:bool = Field(
        title=_("是否是平台租户")
    )

class DefaultTenantOut(ResponseSchema):
    data: DefaultTenantItemOut
    

class SwitchTenantItem(Schema):
    
    id:str = Field(
        title=_("租户ID")
    )
    
    slug:Optional[str] = Field(
        title=_("租户SLUG")
    )
class TenantLogoutOut(ResponseSchema):
    
    refresh:bool = Field(
        title=_("是否刷新页面")
    )
    
    switch_tenant: SwitchTenantItem = Field(
        title=_("切换租户")
    )
    
class TenantLogoutIn(Schema):
    
    password:str = Field(
        title=_("密码"),
        hint=_("请输入您的密码"),
        type="password"
    )