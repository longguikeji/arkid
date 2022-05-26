from typing import Any, List
from pydantic import Field
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.models import App
from arkid.core.extension.app_protocol import AppProtocolExtension
from uuid import UUID

import uuid

AppCreateIn = AppProtocolExtension.create_composite_config_schema(
    'AppCreateIn',
    id=(str,Field(default=uuid.uuid4().hex, hidden=True, readonly=True))
)


class AppCreateOut(ResponseSchema):
    pass

class AppListItemOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo', 'type']

class AppListOut(ResponseSchema):
    data: List[AppListItemOut]
    
AppItemOut = AppProtocolExtension.create_composite_config_schema(
    'AppItemOut',
    id=(Any,Field(readonly=True))
)
    
class AppOut(ResponseSchema):
    data: AppItemOut
    
AppUpdateIn = AppProtocolExtension.create_composite_config_schema(
    'AppUpdateIn',
    exclude=["id"]
)

class AppUpdateOut(ResponseSchema):
    pass