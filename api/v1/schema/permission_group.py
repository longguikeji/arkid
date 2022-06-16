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


class PermissionGroupListSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'is_system']


class PermissionGroupDetailSchemaOut(ModelSchema):

    parent_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category']


class PermissionGroupSchemaOut(Schema):
    permission_group_id: str


class PermissionGroupSchemaIn(ModelSchema):

    app_id: str
    parent_id: str = None

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