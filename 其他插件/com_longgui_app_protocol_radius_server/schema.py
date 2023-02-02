from ninja import Schema
from arkid.core.translation import gettext_default as _
from pydantic import Field

class RadiusServerBaseSchema(Schema):

    auth_url: str = Field(title=_('Auth Url', 'Server Auth Url'), readonly='readonly' ,default='/api/v1/tenant/{tenant_id}/com_longgui_app_protocol_radius_server/radius_login/')

class RadiusLoginSchemaIn(Schema):

    username: str = Field(title=_('Username', '用户名'), default='')
    password: str = Field(title=_('Password', '密码'), default='')
