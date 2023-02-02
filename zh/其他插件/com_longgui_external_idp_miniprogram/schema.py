from ninja import Schema
from pydantic import Field
from arkid.core.translation import gettext_default as _


class ExternalIdpMiniprogramSchema(Schema):
    app_id: str = Field(title=_('App ID', '应用ID'))
    app_secret: str = Field(title=_('Secret ID', '应用密钥'))

    login_url: str = Field(title=_('Login URL', '登录URL'), readonly=True, default='')
    bind_url: str = Field(title=_('Bind URL', '绑定URL'), readonly=True, default='')