#!/usr/bin/env python3

from typing import List
from pydantic import Field, UUID4
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.core.schema import ResponseSchema


class ThirdAuthListItemOut(Schema):

    id: UUID4
    name: str = Field(title=_("名称"))
    type: str = Field(title=_("类型"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


class ThirdAuthListOut(ResponseSchema):
    data: List[ThirdAuthListItemOut]


class ThirdAuthOut(ResponseSchema):
    data: ExternalIdpExtension.create_composite_config_schema('ThirdAuthDataOut')


ThirdAuthCreateIn = ExternalIdpExtension.create_composite_config_schema(
    'ThirdAuthCreateIn', exclude=['id']
)


class ThirdAuthCreateOut(ResponseSchema):
    pass


ThirdAuthUpdateIn = ExternalIdpExtension.create_composite_config_schema(
    'ThirdAuthUpdateIn', exclude=['id']
)


class ThirdAuthUpdateOut(ResponseSchema):
    pass


class ThirdAuthDeleteOut(ResponseSchema):
    pass
