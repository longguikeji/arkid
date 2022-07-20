from typing import List
from ninja import Schema
from pydantic import Field
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.impower_rule import ImpowerRuleBaseExtension


class PermissionRuleListItemOut(Schema):

    id: str
    name: str = Field(title=_("配置名称"))
    type: str = Field(title=_("规则类型"))
    extension_name: str = Field(title=_("所属插件"))
    extension_package: str = Field(title=_("所属插件标识"))

class PermissionRuleListOut(ResponseSchema):
    data: List[PermissionRuleListItemOut]

class PermissionRuleOut(ResponseSchema):
    data: ImpowerRuleBaseExtension.create_composite_config_schema(
        'PermissionRuleDataOut',
        exclude=['id']
    )

PermissionRuleCreateIn = ImpowerRuleBaseExtension.create_composite_config_schema(
    'PermissionRuleCreateIn',
    exclude=['id']
)

class PermissionRuleCreateOut(ResponseSchema):
    pass

PermissionRuleUpdateIn = ImpowerRuleBaseExtension.create_composite_config_schema(
    'PermissionRuleUpdateIn',
    exclude=['id']
)

class PermissionRuleUpdateOut(ResponseSchema):
    pass

class PermissionRuleDeleteOut(ResponseSchema):
    pass