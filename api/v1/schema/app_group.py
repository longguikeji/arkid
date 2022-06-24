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
            path='/api/v1/tenant/{tenant_id}/app_groups/?parent_id={id}',
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


class AppGroupItemParentOut(Schema):
    id:UUID = Field(
        hidden=True
    )
    name:str

class AppGroupItemOut(Schema):
    id:UUID = Field(
        readonly=True
    )
    
    name: str = Field(
        title=_("分组名称")
    )
    
    parent:Optional[AppGroupItemParentOut] = Field(
        page=select_appgroup_parent_page.tag,
        title=_("上级应用分组"),
    )

class AppGroupOut(ResponseSchema):
    data: AppGroupItemOut
    
    
class AppGroupCreateOut(ResponseSchema):
    pass

class AppGroupCreateParentIn(Schema):
    id:UUID = Field(
        hidden=True
    )
    name:str

class AppGroupCreateIn(ModelSchema):

    parent:Optional[AppGroupCreateParentIn] = Field(
        page=select_appgroup_parent_page.tag,
        default=None,
        title=_("上级应用分组")
    )

    class Config:
        model = AppGroup
        model_fields = ['name']
        
class AppGroupUpdateParentIn(Schema):
    id:UUID = Field(
        hidden=True
    )
    name:str
    
class AppGroupUpdateIn(ModelSchema):
    
    parent: Optional[AppGroupUpdateParentIn] = Field(
        title=_("上级用户分组"),
        page=select_appgroup_parent_page.tag,
    )
    
    class Config:
        model = AppGroup
        model_fields = ["name"]
        
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
        page=select_appgroup_parent_page.tag,
        type="array"
    )
    
class AppGroupAppUpdateOut(ResponseSchema):
    pass

class AppGroupExcludeAppsItemOut(Schema):
    id: UUID
    name: str

class AppGroupExcludeAppsOut(ResponseSchema):
    items: List[AppGroupExcludeAppsItemOut]

