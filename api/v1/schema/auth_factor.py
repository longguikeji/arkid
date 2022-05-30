from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.schema import ResponseSchema


class AuthFactorListItemOut(Schema):

    id: str
    name: str = Field(title=_("配置名称"))
    type: str = Field(title=_("认证类型"))
    extension_name: str = Field(title=_("所属插件"))
    extension_package: str = Field(title=_("所属插件标识"))

class AuthFactorListOut(ResponseSchema):
    data: List[AuthFactorListItemOut]

class AuthFactorOut(ResponseSchema):
    data: AuthFactorExtension.create_composite_config_schema(
        'AuthFactorDataOut'
    )

AuthFactorCreateIn = AuthFactorExtension.create_composite_config_schema(
    'AuthFactorCreateIn',
    exclude=['id']
)

class AuthFactorCreateOut(ResponseSchema):
    pass


AuthFactorUpdateIn = AuthFactorExtension.create_composite_config_schema(
    'AuthFactorUpdateIn'
)

class AuthFactorUpdateOut(ResponseSchema):
    pass

class AuthFactorDeleteOut(ResponseSchema):
    pass