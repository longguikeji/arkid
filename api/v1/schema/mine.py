from uuid import UUID
from arkid.core.schema import ResponseSchema
from ninja import ModelSchema, Schema
from typing import List, Optional
from arkid.core.models import App, AppGroup, Message, Tenant, User, Permission
from pydantic import Field
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _


class MineAppItem(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'logo', 'name','url','description','type']
class MineAppsOut(ResponseSchema):
    data:Optional[List[MineAppItem]]


class ProfileTenantOut(Schema):

    id:UUID = Field(title='ID', hidden=True)

    slug:Optional[str] = Field(title='slug', hidden=True)

    name:str = Field(title='name', hidden=True)
    
    is_platform_tenant:bool = Field(title=_("是否是平台租户"),hidden=True,default=False,readonly=True)

class ProfileSchemaOut(Schema):
    
    id:UUID = Field(title='ID', hidden=True)
    username:str = Field(title='用户名',readonly=True)
    avatar:Optional[str] = Field(title=_('头像'))
    tenant:ProfileTenantOut = Field(title=_("租户"),hidden=True)

class ProfileSchemaFinalOut(ResponseSchema):
    data:Optional[ProfileSchemaOut]
class ProfileSchemaIn(ModelSchema):
    class Config:
        model = User
        model_fields = ['avatar']


class MineTenantListItemOut(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ["id", "name", "slug", "icon"]

class MinePermissionListSchemaOut(Schema):

    id: UUID = Field(hidden=True)
    name: str
    # app_name: str = Field(default=None, alias="app.name", title=_("应用名称"))
    category: str
    sort_id: int = Field(hidden=True)
    in_current: bool = Field(item_action={"path":"/api/v1/mine/tenant/{tenant_id}/permissions/{permission_id}/add_permisssion", "method":actions.FrontActionMethod.GET.value, "close": False})
    # is_system: bool
    # is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value})

    # class Config:
    #     model = Permission
    #     model_fields = ['id', 'name', 'category', 'is_system']


class MineTenantListOut(ResponseSchema):
    data: List[MineTenantListItemOut]


class MineLogoutOut(ResponseSchema):
    
    refresh:bool = Field(
        title=_("是否刷新页面")
    )
    
class MineSwitchTenantItem(Schema):
    
    id:str = Field(
        title=_("租户ID")
    )
    
    slug:Optional[str] = Field(
        title=_("租户SLUG")
    )
class MineSwitchTenantOut(ResponseSchema):
    
    refresh:bool = Field(
        title=_("是否刷新页面")
    )
    
    switch_tenant: MineSwitchTenantItem = Field(
        title=_("切换租户")
    )
    
class MineAppGroupListItemOut(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ['id', 'name']
        
class MineAppGroupListOut(ResponseSchema):
    data:List[MineAppGroupListItemOut]
    
class MineAppListItemOut(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'logo', 'name','url','description','type']
        
class MineAppListOut(ResponseSchema):
    data:List[MineAppListItemOut]
    

class MineUnreadMessageListItemOut(ModelSchema):
    class Config:
        model = Message
        model_fields = ["id","title","content"]
        
class MineUnreadMessageListOut(ResponseSchema):
    data:List[MineAppGroupListItemOut]
    
class MineUnreadMessageOut(ModelSchema):
    class Config:
        model=Message
        model_fields = ["id","title","content","created","url"]