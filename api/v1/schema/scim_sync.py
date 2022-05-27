#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.scim_sync import ScimSyncExtension
from arkid.core.schema import ResponseSchema


class ScimSyncListItemOut(Schema):

    id: str
    type: str = Field(title=_("类型"))
    name: str = Field(title=_("名称"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


class ScimSyncListOut(ResponseSchema):
    data: List[ScimSyncListItemOut]


class ScimSyncOut(ResponseSchema):
    data: ScimSyncExtension.create_composite_config_schema('ScimSyncDataOut')


ScimSyncCreateIn = ScimSyncExtension.create_composite_config_schema(
    'ScimSyncCreateIn', exclude=['id']
)


class ScimSyncCreateOut(ResponseSchema):
    pass


ScimSyncUpdateIn = ScimSyncExtension.create_composite_config_schema(
    'ScimSyncUpdateIn', exclude=['id']
)


class ScimSyncUpdateOut(ResponseSchema):
    pass


class ScimSyncDeleteOut(ResponseSchema):
    pass
