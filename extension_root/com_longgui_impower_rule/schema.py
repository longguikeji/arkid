from uuid import UUID
from ninja import Field
from typing import List, Optional
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core import pages, actions

app_page = pages.TablePage(select=True, name='应用列表')
app_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/',
        method=actions.FrontActionMethod.GET
    )
)

app_permission_page = pages.TablePage(name=_("该应用权限"), select=True)
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
    id:UUID = Field(hidden=True)
    name:str

class ImpowerRuleCreateIn(Schema):

    regular: str = Field(
        title=_("规则")
    )

    app: Optional[ImpowerRuleAppCreateInItem] = Field(
        page=app_page.tag,
        title=_("选择应用"),
    )

    permissions: Optional[List[ImpowerRulePermissionCreateInItem]] = Field(
        page=app_permission_page.tag,
        title=_("选择权限")
    )
