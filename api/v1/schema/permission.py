from enum import Enum
from uuid import UUID
from ninja import Field
from ninja import Schema
from ninja import ModelSchema
from typing import List, Optional
from arkid.core import pages,actions
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
from arkid.core.models import Permission, SystemPermission

select_app_page = pages.TablePage(select=True,name=_("选择应用"))

pages.register_front_pages(select_app_page)

select_app_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET
    )
)

class PermissionsListSchemaOut(ModelSchema):

    app_name: str = Field(default=None, alias="app.name", title=_("应用"))
    sort_id: int = Field(hidden=True)
    # is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value}, title=_("是否授权给其它租户"))
    category: str = Field(title=_("分类"),notranslation=True)
    operation_id: str = Field(default='', title=_("操作ID"))

    class Config:
        model = Permission
        model_fields = ['id', 'operation_id', 'name', 'is_system']


class AppPermissionsItemSchemaOut(Schema):

    id: UUID = Field(hidden=True)
    operation_id: str = Field(default='', title=_("操作ID"))
    name: str = Field(title=_("名称"))
    app_name: str = Field(default=None, alias='app.name', title=_("应用"))
    sort_id: int = Field(hidden=True)
    category: str = Field(title=_("分类"),notranslation=True)


class AppPermissionsListSchemaOut(ResponseSchema):
    data: List[AppPermissionsItemSchemaOut]

class UserAppLastPermissionsItemSchemaOut(Schema):

    id: UUID = Field(default=None)
    operation_id: str = Field(default='', title=_("操作ID"))
    name: str = Field(title=_("名称"))
    is_system: bool = Field(title=_("是否是系统权限"))
    app_name: str = Field(default=None, alias="app.name", title=_("应用"))
    sort_id: int = Field(hidden=True)
    # is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value}, title=_("是否授权给其它租户"))
    category: str = Field(title=_("分类名称"), notranslation=True)
    in_current: bool = Field(title=_("是否已拥有"))

class UserAppLastPermissionsSchemaOut(ResponseSchema):
    data: List[UserAppLastPermissionsItemSchemaOut]


class PermissionSchemaOut(Schema):
    permission_id: str


class PermissionCategory(str, Enum):
    entry = 'entry'
    api = 'api'
    data = 'data'
    group = 'group'
    ui = 'ui'
    other = 'other'


class PermissionCreateItemSchemaIn(Schema):

    id:UUID = Field(hidden=True)
    name:str


class PermissionListQueryIn(Schema):

    app_id: Optional[str] = Field(hidden=True, default=None)
    select_user_id: Optional[str] = Field(hidden=True, default=None)
    group_id: Optional[str] = Field(hidden=True, default=None)
    app_name: Optional[str] = Field(title=_("应用名称"), default=None)
    category: Optional[PermissionCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)


class AppPermissionListQueryIn(Schema):

    category: Optional[PermissionCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)

class UserGroupLastPermQueryIn(Schema):

    app_id: Optional[str] = Field(hidden=True, default=None)
    usergroup_id: Optional[str] = Field(hidden=True, default=None)
    app_name: Optional[str] = Field(title=_("应用名称"), default=None)
    category: Optional[PermissionCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)

class GroupPermissionListQueryIn(Schema):

    select_usergroup_id: Optional[str] = Field(hidden=True, default=None)
    app_name: Optional[str] = Field(title=_("应用名称"), default=None)
    category: Optional[PermissionCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)

class UserPermissionLastQueryIn(Schema):

    app_id: Optional[str] = Field(hidden=True, default=None)
    user_id: Optional[str] = Field(hidden=True, default=None)
    app_name: Optional[str] = Field(title=_("应用名称"), default=None)
    category: Optional[PermissionCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)

class PermissionCreateSchemaIn(ModelSchema):

    app: PermissionCreateItemSchemaIn = Field(
        page=select_app_page.tag,
        title=_("应用")
    )

    category: PermissionCategory = 'other'

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionEditSchemaIn(Schema):

    name: str
    category: str
    # class Config:
    #     model = Permission
    #     model_fields = ['name', 'category']


class PermissionDetailSchemaOut(ModelSchema):

    id: UUID = Field(hidden=True)
    # parent_id: UUID = Field(default=None)
    category: PermissionCategory

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionDetailOut(ResponseSchema):
    data: Optional[PermissionDetailSchemaOut]


class PermissionStrSchemaOut(Schema):
    result: str


class PermissionBatchSchemaIn(Schema):
    data: List[str]
