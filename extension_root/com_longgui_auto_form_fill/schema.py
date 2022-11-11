from ninja import Schema
from enum import Enum
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class SAVE_TYPE(str, Enum):
    database = _('database', '数据库')
    web = _('web', '浏览器')

class AutoFormFillSettingsConfigSchema(Schema):

    save_type: SAVE_TYPE = Field(default='web', title=_('Save Type', '存储位置'))
