from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_rule import AuthRuleExtension
from arkid.core.schema import ResponseSchema


class AuthRuleListItemOut(Schema):

    id: str
    name: str = Field(title=_("配置名称"))
    type: str = Field(title=_("规则类型"))
    extension_name: str = Field(title=_("所属插件"))
    extension_package: str = Field(title=_("所属插件标识"))

class AuthRuleListOut(ResponseSchema):
    data: List[AuthRuleListItemOut]

class AuthRuleOut(ResponseSchema):
    data: AuthRuleExtension.create_composite_config_schema(
        'AuthRuleDataOut'
    )

AuthRuleCreateIn = AuthRuleExtension.create_composite_config_schema(
    'AuthRuleCreateIn',
    exclude=['id']
)

class AuthRuleCreateOut(ResponseSchema):
    pass


AuthRuleUpdateIn = AuthRuleExtension.create_composite_config_schema(
    'AuthRuleUpdateIn'
)

class AuthRuleUpdateOut(ResponseSchema):
    pass

class AuthRuleDeleteOut(ResponseSchema):
    pass