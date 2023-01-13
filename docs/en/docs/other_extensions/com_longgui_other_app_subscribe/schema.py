from typing import List, Optional
from ninja import Field, Schema
from arkid.core import actions
from arkid.core.extension import create_extension_schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class GetAllAppsItemOut(Schema):
    id: str = Field(
        hidden=True,
        title=_("ID")
    )
    name:str = Field(
        title=_("应用名称")
    )
    logo:str
    is_subscribed:bool =Field(
        title=_("是否已订阅"),
        item_action={
            "path":'/api/v1/tenant/{tenant_id}/com_longgui_other_app_subscribe/app/{id}/change_subscribe_status/',
            "method":actions.FrontActionMethod.POST.value
        }
    )
    
class GetAllAppsOut(ResponseSchema):
    data:List[GetAllAppsItemOut]