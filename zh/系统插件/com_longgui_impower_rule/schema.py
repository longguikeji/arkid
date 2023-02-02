from uuid import UUID
from enum import Enum
from ninja import Field
from typing import List, Optional
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core import pages, actions
from arkid.core.extension import create_extension_page

user_field_page = create_extension_page(__file__,pages.TablePage, select=True, name='用户字段列表')
user_field_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_fields/',
        method=actions.FrontActionMethod.GET
    )
)

app_page = create_extension_page(__file__,pages.TablePage, select=True, name='应用列表')
app_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/',
        method=actions.FrontActionMethod.GET
    )
)

app_permission_page = create_extension_page(__file__,pages.TablePage, select=True, name='该应用权限')
app_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permissions?app_id={app_id}',
        method=actions.FrontActionMethod.GET
    ),
)

class ImpowerRuleAppCreateInItem(Schema):
    id:str = Field(hidden=True)
    name:str

class ImpowerRulePermissionCreateInItem(Schema):
    id:str = Field(hidden=True)
    sort_id: int = Field(hidden=True)
    name:str

class ImpowerRuleMatchFieldCreateInItem(Schema):
    id:str = Field(hidden=True)
    name:str

class MatchSymbol(str, Enum):
    等于 = '等于'
    # 大于 = '大于'
    # 小于 = '小于'

class ImpowerRuleCreateIn(Schema):

    matchfield: Optional[ImpowerRuleMatchFieldCreateInItem] = Field(
        page=user_field_page.tag,
        title=_("选择匹配字段"),
    )
    matchsymbol: MatchSymbol = Field(
        title=_("选择匹配符号"),
        default='等于'
    )
    matchvalue: str = Field(
        title=_("输入匹配值"),
    )

    app: Optional[ImpowerRuleAppCreateInItem] = Field(
        page=app_page.tag,
        title=_("选择应用"),
    )

    permissions: Optional[List[ImpowerRulePermissionCreateInItem]] = Field(
        page=app_permission_page.tag,
        title=_("选择权限")
    )
