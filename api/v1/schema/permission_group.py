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

class PermissionListSchemaOut(ModelSchema):

    class Config:
        model = SystemPermission
        model_fields = ['id', 'name', 'category', 'is_system']


class PermissionListSelectSchemaOut(Schema):

    id: UUID = Field(default=None)
    in_current: bool = Field(title=_("是否在当前分组里"), hidden=True)
    name: str
    category: str
    is_system: bool

class PermissionListDataSelectSchemaOut(ResponseSchema):
    data: List[PermissionListSelectSchemaOut]

class PermissionGroupPermissionSchemaIn(Schema):
    data: List[str]