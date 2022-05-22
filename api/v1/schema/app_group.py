from typing import List, Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from requests import Response
from arkid.core.models import App, User, AppGroup
from arkid.core.schema import ResponseSchema
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _

select_appgroup_parent_page = pages.TreePage(select=True,name=_("选择上级分组"))

pages.register_front_pages(select_appgroup_parent_page)

select_appgroup_parent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/',
        method=actions.FrontActionMethod.GET
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/app_groups/',
            method=actions.FrontActionMethod.GET
        )
    ],
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
    id:UUID = Field(
        readonly=True
    )

    parent: Optional[UUID] = Field(
        field="id",
        page=select_appgroup_parent_page.tag,
        link="name"
    )
    
    class Config:
        model = AppGroup
        model_fields = ['id', 'name', "parent"]

class AppGroupOut(ResponseSchema):
    data: AppGroupItemOut
    
class AppGroupCreateOut(ResponseSchema):
    pass

class AppGroupCreateIn(ModelSchema):

    parent: str = Field(
        field="id",
        page=select_appgroup_parent_page.tag,
        link="name",
        default=None,
        title=_("上级应用分组")
    )

    class Config:
        model = AppGroup
        model_fields = ['name']
        
class AppGroupUpdateIn(ModelSchema):
    class Config:
        model = AppGroup
        model_fields = ["name","parent"]
        
class AppGroupUpdateOut(Schema):
    pass

class AppGroupDeleteOut(ResponseSchema):
    pass

class AppGroupAppListItemOut(ModelSchema):
    class Config:
        model = App
        model_fields = ['id', 'name']

class AppGroupAppListOut(ResponseSchema):
    data:List[AppGroupAppListItemOut]


class AppGroupDetailItemOut(ModelSchema):

    parent_id: UUID = None

    class Config:
        model = AppGroup
        model_fields = ['id', 'name',"parent"]

class AppGroupDetailOut(ResponseSchema):
    data:AppGroupDetailItemOut

        
class AppGroupAppRemoveOut(ResponseSchema):
    pass


select_appgroup_excluded_apps_page = pages.TablePage(select=True,name=_("添加应用指分组"))

pages.register_front_pages(select_appgroup_excluded_apps_page)

select_appgroup_excluded_apps_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_groups/{id}/select_apps/',
        method=actions.FrontActionMethod.GET
    )
)

class AppGroupAppUpdateIn(Schema):
    
    apps: List[str] = Field(
        field="id",
        page=select_appgroup_parent_page.tag,
        link="name",
        select_status = "status",
        type="array"
    )
    
class AppGroupAppUpdateOut(ResponseSchema):
    pass

class AppGroupSelectAppsItemOut(Schema):
    id: str
    name: str
    status: bool

class AppGroupSelectAppsOut(ResponseSchema):
    data: List[AppGroupSelectAppsItemOut]

