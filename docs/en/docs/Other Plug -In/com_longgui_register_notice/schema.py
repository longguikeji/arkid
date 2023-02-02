from ninja import Schema
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class RegisterNoticeConfigSchema(Schema):

    caption: str = Field(default='', title=_('caption', '标题'))
    content: str = Field(default='', title=_('content', '内容'), format='textarea')
