from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.schema import ResponseSchema


class AuthFactorListItemOut(Schema):

    id: str
    type: str = Field(title=_("类型"))
    name: str = Field(title=_("名称"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))

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