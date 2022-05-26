from enum import Enum
from ninja import Schema
from oauth2_provider.models import Application
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field


class GithubConfigSchema(Schema):

    client_id: str = Field(title=_('client id', '客户端id'))
    client_secret: str = Field(title=_('client secret', '客户端密钥'))
    img_url: str = Field(title=_('Img Url', 'Github图标url'), readonly=True, default='')
    login_url: str = Field(
        title=_('Login Url', 'Github登录url'), readonly=True, default=''
    )
    callback_url: str = Field(
        title=_('Callback Url', 'Github回调url'), readonly=True, default=''
    )
    bind_url: str = Field(title=_('Bind Url', 'Github绑定url'), readonly=True, default='')
