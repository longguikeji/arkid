from typing import Any, List
from pydantic import Field
from ninja import ModelSchema, Schema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from arkid.core.models import App
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.extension.models import TenantExtensionConfig
from uuid import UUID

import uuid

AppCreateIn = AppProtocolExtension.create_composite_config_schema(
    'AppCreateIn',
    id=(str, Field(default=uuid.uuid4().hex, hidden=True, readonly=True))
)

# class AppCreateIn(ModelSchema):
#     class Config:
#         model = App
#         model_fields = ['name', 'url', 'logo']


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
    id=(Any, Field(readonly=True))
)


class AppOut(ResponseSchema):
    data: AppItemOut


AppUpdateIn = AppProtocolExtension.create_composite_config_schema(
    'AppUpdateIn',
    exclude=["id"]
)


class AppUpdateOut(ResponseSchema):
    pass


AppSchemaOut = AppProtocolExtension.create_composite_config_schema(
    'AppSchemaOut')


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


AppProtocolConfigIn = AppProtocolExtension.create_composite_config_schema(
    'AppProtocolConfigIn',
    exclude=["name", "logo", "url", 'description'],
)

AppProtocolConfigItemOut = AppProtocolExtension.create_composite_config_schema(
    'AppProtocolConfigItemOut',
    id=(UUID,Field(hidden=True)),
    exclude=["name", "logo", "url", 'description'],
)


class AppProtocolConfigOut(ResponseSchema):
    data: AppProtocolConfigItemOut


class CreateAppProfileIn(ModelSchema):

    class Config:
        model = App
        model_fields = ['name', 'url', 'logo', 'description']


class CreateAppProfileOut(ResponseSchema):
    pass


class AppProfileItemOut(ModelSchema):

    class Config:
        model = App
        model_fields = ['name', 'url', 'logo', 'description']


class AppProfileOut(ResponseSchema):
    data: AppProfileItemOut


class UpdateAppProfileIn(ModelSchema):

    class Config:
        model = App
        model_fields = ['name', 'url', 'logo', 'description']


class UpdateAppProfileOut(ResponseSchema):
    pass
