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
from api.v1.pages.permission_manage.permission_group import select_app_page, select_permission_group_page



class PermissionGroupListSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'is_system']

class PermissionGroupDetailInfoParentOut(Schema):
    id:UUID = Field(
        hidden=True,
    )
    name:str
    
class PermissionGroupDetailInfoSchemaOut(ModelSchema):

    id: UUID = Field(hidden=True)
    parent: Optional[PermissionGroupDetailInfoParentOut] = Field(
        page=select_permission_group_page.tag,
        title=_("父权限分组")
    )

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionGroupDetailSchemaOut(ResponseSchema):
    data: PermissionGroupDetailInfoSchemaOut


class PermissionGroupSchemaOut(Schema):
    permission_group_id: str

class UserGroupCreateParentIn(Schema):
    id:UUID = Field(hidden=True)
    name:str

class UserGroupCreateAppIn(Schema):
    id:str = Field(hidden=True)
    name:str

class PermissionGroupSchemaIn(ModelSchema):

    app: UserGroupCreateAppIn = Field(
        # field="id",
        page=select_app_page.tag,
        # link="app",
        # default=None,
        title=_("应用")
    )
    parent: UserGroupCreateParentIn = Field(
        default=None,
        # field="id",
        page=select_permission_group_page.tag,
        # link="name",
        title=_("父权限分组")
    )

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionGroupEditSchemaIn(Schema):

    parent: UserGroupCreateParentIn = Field(
        default=None,
        # field="id",
        page=select_permission_group_page.tag,
        # link="name",
        title=_("父权限分组")
    )
    name: str

    # class Config:
    #     model = Permission
    #     model_fields = ['name']

class PermissionListSchemaOut(Schema):
    category: str = Field(title=_("分类"),notranslation=True)
    operation_id: str = Field(default='', title=_("操作ID"))
    id: UUID = Field(title=_("id"))
    name: str = Field(title=_("名称"))
    is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value}, title=_("是否授权给其它租户"))
    is_open_other_user: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_other_user_open", "method":actions.FrontActionMethod.POST.value}, title=_("是否租户内所有人可见"))
    is_system: bool = Field(title=_("是否是系统权限"))
    # class Config:
    #     model = SystemPermission
    #     model_fields = ['id', 'name', 'is_system']

class PermissionGroupCategory(str, Enum):
    entry = 'entry'
    api = 'api'
    data = 'data'
    group = 'group'
    ui = 'ui'
    other = 'other'

class PermissionGroupListQueryIn(Schema):
    category: Optional[PermissionGroupCategory] = Field(title=_("分类"), default=None)
    name: Optional[str] = Field(title=_("权限名称"), default=None)
    operation_id: Optional[str] = Field(title=_("操作ID"), default=None)


class PermissionListSelectSchemaOut(Schema):

    id: UUID = Field(default=None)
    in_current: bool = Field(title=_("是否在当前分组里"), hidden=True)
    name: str
    category: str
    is_system: bool = Field(title=_("是否是系统权限"))

class PermissionListDataSelectSchemaOut(ResponseSchema):
    data: List[PermissionListSelectSchemaOut]

class PermissionGroupPermissionSchemaIn(Schema):
    data: List[str]