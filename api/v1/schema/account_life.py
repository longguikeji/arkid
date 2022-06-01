#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.extension.account_life import AccountLifeExtension
from arkid.core.schema import ResponseSchema


class AccountLifeListItemOut(Schema):

    id: str
    type: str = Field(title=_("类型"))
    name: str = Field(title=_("名称"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


class AccountLifeListOut(ResponseSchema):
    data: List[AccountLifeListItemOut]


class AccountLifeOut(ResponseSchema):
    data: AccountLifeExtension.create_composite_config_schema(
        'AccountLifeDataOut', exclude=['id']
    )


AccountLifeCreateIn = AccountLifeExtension.create_composite_config_schema(
    'AccountLifeCreateIn', exclude=['id']
)


class AccountLifeCreateOut(ResponseSchema):
    pass


AccountLifeUpdateIn = AccountLifeExtension.create_composite_config_schema(
    'AccountLifeUpdateIn', exclude=['id']
)


class AccountLifeUpdateOut(ResponseSchema):
    pass


class AccountLifeDeleteOut(ResponseSchema):
    pass


class AccountLifeCrontabSchema(Schema):
    crontab: str = Field(default='0 1 * * *', title=_('Crontab', '定时运行时间'))
    max_retries: int = Field(default=3, title=_('Max Retries', '重试次数'))
    retry_delay: int = Field(default=60, title=_('Retry Delay', '重试间隔(单位秒)'))


class AccountLifeCrontabOut(ResponseSchema):
    data: AccountLifeCrontabSchema
