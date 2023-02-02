from typing import List, Optional, Any
from uuid import UUID
from ninja import Field, Schema
from arkid.core import actions, pages
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

select_app_page = pages.TablePage(select=True,name=_("选择应用"))
mine_select_app_page = pages.TablePage(name=_("选择应用"),select=True)

class AppIn(Schema):
    id:str = Field(hidden=True)
    name:str

class AppMultiAccountSettingSchema(Schema):

    app:AppIn = Field(
        title=_("应用"),
        page=select_app_page.tag,
    )

    bind_url:str = Field(
        title=_("绑定接口地址")
    )

    unbind_url:Optional[str] = Field(
        title=_("解绑接口地址")
    )

class AppMultiAccountSettingOutSchema(ResponseSchema):
    pass

class AppListItemOut(Schema):
    id:str = Field(hidden=True)
    name:str = Field(title=_("名称"))

class AppAccountListItemOut(Schema):
    id:str = Field(hidden=True)
    name:str = Field(title=_("应用名称"))
    username:str = Field(title=_("用户名"))

class UserAppAccountListItemOut(Schema):
    platform_user_id:str
    token: Any
class UserAppAccountListOut(ResponseSchema):
    data:List[UserAppAccountListItemOut]

class AppMultiAccountSettingUpdateSchema(Schema):
    
    app:str = Field(
        title=_("应用"),
        readonly=True,
    )

    bind_url:str = Field(
        title=_("绑定接口地址")
    )

    unbind_url:Optional[str] = Field(
        title=_("解绑接口地址")
    )

class AppMultiAccountSettingListFilterSchema(Schema):
    app__name:Optional[str] = Field(
        title=_("应用名称"),
    )

class AppMultiAccountSettingListItemOutSchema(Schema):
    
    id:str

    app:str = Field(
        title=_("应用")
    )

    bind_url:str = Field(
        title=_("绑定接口地址")
    )

    unbind_url:Optional[str] = Field(
        title=_("解绑接口地址")
    )

class AppMultiAccountSettingDetailItemOutSchema(Schema):
    app:str = Field(
        title=_("应用"),
        readonly=True,
    )

    bind_url:str = Field(
        title=_("绑定接口地址")
    )

    unbind_url:Optional[str] = Field(
        title=_("解绑接口地址")
    )

class AppMultiAccountSettingDetailOutSchema(ResponseSchema):
    data:AppMultiAccountSettingDetailItemOutSchema

class AppMultiAccountSettingListOutSchema(ResponseSchema):
    items:List[AppMultiAccountSettingListItemOutSchema]

class BindInSchema(Schema):

    app:AppIn = Field(
        title=_("应用"),
        page=mine_select_app_page.tag,
    )

    username:str = Field(
        title=_("用户名")
    )

    password:str = Field(
        title=_("密码"),
        format="password"
    )