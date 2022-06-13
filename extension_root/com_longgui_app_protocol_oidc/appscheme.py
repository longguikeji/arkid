from enum import Enum
from ninja import Schema
from oauth2_provider.models import Application
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class CLIENT_TYPE(str, Enum):
    confidential = _('confidential', '私密')
    public = _('public','公开')


class GRANT_TYPE(str, Enum):
    authorization_code = _('authorization-code', '私密')
    implicit = _('implicit','公开')
    password = _('password','密码')
    client_credentials = _('client-credentials','客户端凭据')
    openid_hybrid = _('openid-hybrid','OpenID链接')


class ConfigBaseSchema(Schema):

    skip_authorization: bool = Field(title=_('skip authorization', '是否跳过验证'), default=False)
    redirect_uris: str = Field(title=_('redirect uris', '回调地址'))
    client_type: CLIENT_TYPE = Field(title=_('client type','客户端是否公开'))
    grant_type: GRANT_TYPE = Field(title=_('type','授权类型'))


class Oauth2ConfigSchema(ConfigBaseSchema):

    # 输出的比输入的额外多了一些字段
    client_id: str = Field(title=_('client id','客户端id'), readonly=True, default='')
    client_secret: str = Field(title=_('client secret','客户端密钥'), readonly=True, default='')
    authorize: str = Field(title=_('authorize','授权url'), readonly=True, default='')
    token: str = Field(title=_('token','获取token地址'), readonly=True, default='')
    userinfo: str = Field(title=_('userinfo','用户信息地址'), readonly=True, default='')
    logout: str = Field(title=_('logout', '退出登录地址'), readonly=True, default='')


# class OAuth2AppSchema(AppBaseSchema):

#     data: Oauth2ConfigSchema = Field(title=_('data', '数据'))


class ALGORITHM_TYPE(str, Enum):

    RS256 = _('RS256','RS256加密')
    HS256 = _('HS256','HS256加密')


class OIDCConfigSchema(ConfigBaseSchema):

    algorithm: ALGORITHM_TYPE = Field(title=_('algorithm','加密类型'))
    client_id: str = Field(title=_('client id','客户端id'), readonly=True, default='')
    client_secret: str = Field(title=_('client secret','客户端密钥'), readonly=True, default='')
    authorize: str = Field(title=_('authorize','授权url'), readonly=True, default='')
    token: str = Field(title=_('token','获取token地址'), readonly=True, default='')
    userinfo: str = Field(title=_('userinfo','用户信息地址'), readonly=True, default='')
    logout: str = Field(title=_('logout', '退出登录地址'), readonly=True, default='')

