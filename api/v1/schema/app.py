from typing import Any, List
from pydantic import Field
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.models import App
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.extension.models import TenantExtensionConfig
from uuid import UUID

class AppListItemOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo', 'type']


class AppListOut(ResponseSchema):
    data: List[AppListItemOut]



class AppItemsOut(Schema):

    name: str
    id: str
    is_system: bool


class AppListsOut(ResponseSchema):
    data: List[AppItemsOut]


class AppItemOut(ModelSchema):

    id: UUID = Field(readonly=True)
    
    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo','description']


class AppOut(ResponseSchema):
    data: AppItemOut


class AppUpdateIn(ModelSchema):

    class Config:
        model = App
        model_fields = ['name', 'url', 'logo','description']

class AppUpdateOut(ResponseSchema):
    pass


class AppConfigSchemaOut(Schema):
    app_id: str


class AppListSchemaOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['id', 'name', 'url', 'logo', 'type']


class ConfigSchemaOut(ModelSchema):

    class Config:
        model = TenantExtensionConfig
        model_fields = ['config']


class ConfigOpenApiVersionSchemaOut(Schema):

    version: str = Field(title=_('version', '应用版本'), default='')
    openapi_uris: str = Field(title=_('openapi uris', '接口文档地址'), default='')


class ConfigOpenApiVersionDataSchemaOut(ResponseSchema):

    data: ConfigOpenApiVersionSchemaOut


AppProtocolConfigIn = AppProtocolExtension.create_composite_config_schema(
    'AppProtocolConfigIn',
    exclude=["name", "type", "logo", "url", 'description', 'entry_permission', 'arkstore_app_id'],
)

AppProtocolConfigItemOut = AppProtocolExtension.create_composite_config_schema(
    'AppProtocolConfigItemOut',
    id=(UUID, Field(hidden=True)),
    exclude=["name", "type", "logo", "url", 'description', 'entry_permission', 'arkstore_app_id'],
)


class AppProtocolConfigOut(ResponseSchema):
    data: AppProtocolConfigItemOut


class CreateAppIn(ModelSchema):

    class Config:
        model = App
        model_fields = ['name', 'url', 'logo', 'description']


class CreateAppOut(ResponseSchema):
    pass