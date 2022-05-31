#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auto_auth import AutoAuthExtension
from arkid.core.schema import ResponseSchema


class AutoAuthListItemOut(Schema):

    id: str
    type: str = Field(title=_("类型"))
    # name: str = Field(title=_("名称"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


class AutoAuthListOut(ResponseSchema):
    data: List[AutoAuthListItemOut]


class AutoAuthOut(ResponseSchema):
    data: AutoAuthExtension.create_composite_config_schema('AutoAuthDataOut')


AutoAuthCreateIn = AutoAuthExtension.create_composite_config_schema(
    'AutoAuthCreateIn', exclude=['id']
)


class AutoAuthCreateOut(ResponseSchema):
    pass


AutoAuthUpdateIn = AutoAuthExtension.create_composite_config_schema(
    'AutoAuthUpdateIn', exclude=['id']
)


class AutoAuthUpdateOut(ResponseSchema):
    pass


class AutoAuthDeleteOut(ResponseSchema):
    pass
