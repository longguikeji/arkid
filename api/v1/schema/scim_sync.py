#!/usr/bin/env python3

from typing import List
from pydantic import Field, validator
from ninja import Schema, ModelSchema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.scim_sync import ScimSyncExtension
from arkid.core.schema import ResponseSchema
from arkid.extension.models import TenantExtensionConfig
from arkid.core.models import ScimSyncLog
from datetime import datetime, timedelta, timezone


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


def utc_to_local_datetime(dt: datetime) -> datetime:
    if dt:
        return dt.astimezone(timezone(timedelta(hours=8)))
    else:
        return dt


def utc_to_local_str(dt: datetime) -> str:
    if dt:
        return dt.astimezone(timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%d, %H:%M:%S"
        )
    else:
        return dt


class ScimSyncLogListItemOut(ModelSchema):
    class Config:
        model = ScimSyncLog
        model_fields = [
            'id',
            'start_time',
            'end_time',
            'users_created',
            'users_deleted',
            'groups_created',
            'groups_deleted',
            'error',
        ]

    _normalize_start_time = validator(
        "start_time", check_fields=False, allow_reuse=True
    )(utc_to_local_str)

    _normalize_end_time = validator("end_time", check_fields=False, allow_reuse=True)(
        utc_to_local_str
    )
