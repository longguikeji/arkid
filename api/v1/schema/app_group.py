from typing import List, Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from requests import Response
from arkid.core.models import App, User, AppGroup
from arkid.core.schema import ResponseSchema
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _

select_appgroup_parent_page = pages.TablePage(select=True,name=_("选择上级分组"))

pages.register_front_pages(select_appgroup_parent_page)

select_appgroup_parent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET
    )
)

class AppGroupListQueryIn(Schema):
    parent_id: Optional[str]

class AppGroupListItemOut(ModelSchema):

    class Config:
        model = AppGroup
        model_fields = ['id', 'name']

class AppGroupListOut(ResponseSchema):

    data: List[AppGroupListItemOut]


class AppGroupItemOut(ModelSchema):

    parent_id: str

    class Config:
        model = AppGroup
        model_fields = ['id', 'name', "parent"]

class AppGroupOut(ResponseSchema):
    data: AppGroupItemOut

class AppGroupIn(ModelSchema):

    parent_id: str = Field(
        field="id",
        page=select_appgroup_parent_page.tag,
        link="parent"
    )

    class Config:
        model = AppGroup
        model_fields = ['name']

class AppGroupDeleteOut(ResponseSchema):
    pass

class AppGroupUserListItemOut(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'name']

class AppGroupUserListOut(ResponseSchema):
    data:List[AppGroupUserListItemOut]


class AppGroupDetailItemOut(ModelSchema):

    parent_id: UUID = None

    class Config:
        model = AppGroup
        model_fields = ['id', 'name',"parent"]

class AppGroupDetailOut(ResponseSchema):
    data:AppGroupDetailItemOut


class AppGroupAppItemOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['id', 'name']


class AppGroupAppsOut(ResponseSchema):
    items: List[AppGroupAppItemOut]


class AppGroupUserIn(Schema):
    user_ids: List[str]
