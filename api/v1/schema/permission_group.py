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


class PermissionGroupDetailInfoSchemaOut(ModelSchema):

    parent_id: UUID = Field(
        field="id",
        page=select_permission_group_page.tag,
        link="name",
        default=None,
        show="parent_name",
        title=_("父权限分组")
    )
    parent_name: str = Field(default=None, alias="parent.name", hidden=True)

    class Config:
        model = Permission
        model_fields = ['id', 'name']


class PermissionGroupDetailSchemaOut(ResponseSchema):
    data: PermissionGroupDetailInfoSchemaOut


class PermissionGroupSchemaOut(Schema):
    permission_group_id: str


class PermissionGroupSchemaIn(ModelSchema):

    app_id: UUID = Field(
        field="id",
        page=select_app_page.tag,
        link="app",
        default=None,
        title=_("应用")
    )
    parent_id: UUID = Field(
        field="id",
        page=select_permission_group_page.tag,
        link="name",
        default=None,
        title=_("父权限分组")
    )

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionGroupEditSchemaIn(ModelSchema):

    parent_id: str = None

    class Config:
        model = Permission
        model_fields = ['name']

class PermissionListSchemaOut(ModelSchema):

    class Config:
        model = SystemPermission
        model_fields = ['id', 'name', 'category', 'is_system']


class PermissionListSelectSchemaOut(Schema):

    id: UUID = Field(default=None)
    in_current: bool
    name: str
    category: str
    is_system: bool


class PermissionSchemaIn(Schema):
    permission_id: str