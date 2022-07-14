from uuid import UUID
from arkid.core.schema import ResponseSchema
from ninja import ModelSchema, Schema
from typing import List, Optional
from arkid.core.models import App, Tenant, User, Permission
from pydantic import Field
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _


class MineAppItem(ModelSchema):
    class Config:
        model = App
        model_fields = ['logo', 'name','url','description','type']
class MineAppsOut(ResponseSchema):
    data:Optional[List[MineAppItem]]



class ProfileSchemaOut(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']
    
    id:UUID = Field(title='ID', hidden=True)
    username:str = Field(title='用户名',readonly=True)


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
    in_current: bool = Field(item_action={"path":"/api/v1/mine/tenant/{tenant_id}/permissions/{permission_id}/add_permisssion", "method":actions.FrontActionMethod.GET.value, "off": False})
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