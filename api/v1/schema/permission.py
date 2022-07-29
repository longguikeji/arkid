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

class PermissionListSchemaOut(ModelSchema):

    app_name: str = Field(default=None, alias="app.name", title=_("应用名称"))
    sort_id: int = Field(hidden=True)
    is_open: bool = Field(item_action={"path":"/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open", "method":actions.FrontActionMethod.POST.value}, title=_("是否授权给其它租户"))
    category: str = Field(title=_("分类名称"))

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'is_system', 'is_open']


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
