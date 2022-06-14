#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.core.schema import ResponseSchema
from pydantic import UUID4


class ApproveSystemListItemOut(Schema):

    id: UUID4
    name: str = Field(title=_("名称"))
    type: str = Field(title=_("类型"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


class ApproveSystemListOut(ResponseSchema):
    data: List[ApproveSystemListItemOut]


class ApproveSystemOut(ResponseSchema):
    data: ApproveSystemExtension.create_composite_config_schema(
        'ApproveSystemDataOut', exclude=['id']
    )


ApproveSystemCreateIn = ApproveSystemExtension.create_composite_config_schema(
    'ApproveSystemCreateIn', exclude=['id']
)


class ApproveSystemCreateOut(ResponseSchema):
    pass


ApproveSystemUpdateIn = ApproveSystemExtension.create_composite_config_schema(
    'ApproveSystemUpdateIn', exclude=['id']
)


class ApproveSystemUpdateOut(ResponseSchema):
    pass


class ApproveSystemDeleteOut(ResponseSchema):
    pass
