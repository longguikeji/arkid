from enum import Enum
from ninja import Schema
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class CasConfigSchema(Schema):

    # 输出的比输入的额外多了一些字段
    login: str = Field(title=_('login','登录地址'), readonly=True, default='')
    # logout: str = Field(title=_('logout','退出登录地址'), readonly=True, default='')
    verify: str = Field(title=_('verify','校验地址'), readonly=True, default='')
