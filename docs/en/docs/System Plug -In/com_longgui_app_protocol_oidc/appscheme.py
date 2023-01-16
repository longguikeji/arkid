from enum import Enum
from ninja import Schema
from oauth2_provider.models import Application
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class CLIENT_TYPE(str, Enum):
    confidential = _('confidential', '机密')
    public = _('public','公开')


class GRANT_TYPE(str, Enum):
    authorization_code = _('authorization-code', '授权码模式')
    implicit = _('implicit','简化模式')
    password = _('password','密码模式')
    client_credentials = _('client-credentials','客户端模式')
    openid_hybrid = _('openid-hybrid','OpenID混合模式')

class ConfigBaseSchema(Schema):

    skip_authorization: bool = Field(title=_('skip authorization', '是否隐藏授权页'), default=False)
    redirect_uris: str = Field(title=_('redirect uris', '回调地址'))
    client_type: CLIENT_TYPE = Field(title=_('client type','客户端类型'))
    grant_type: GRANT_TYPE = Field(title=_('type','授权模式'))


class Oauth2ConfigSchema(ConfigBaseSchema):

    # 输出的比输入的额外多了一些字段
    client_id: str = Field(title=_('Client ID','客户端id'), readonly=True, default='')
    client_secret: str = Field(title=_('Client Secret','客户端密钥'), readonly=True, default='')
    authorize: str = Field(title=_('Authorize','授权url'), readonly=True, default='')
    token: str = Field(title=_('Token','获取token地址'), readonly=True, default='')
    userinfo: str = Field(title=_('Userinfo','用户信息地址'), readonly=True, default='')
    logout: str = Field(title=_('Logout', '退出登录地址'), readonly=True, default='')
    issuer_url: str = Field(title=_('Issuer', 'Issuer'), readonly=True, default='')


# class OAuth2AppSchema(AppBaseSchema):

#     data: Oauth2ConfigSchema = Field(title=_('data', '数据'))


class ALGORITHM_TYPE(str, Enum):

    RS256 = _('RS256','RS256加密')
    HS256 = _('HS256','HS256加密')


class OIDCConfigSchema(ConfigBaseSchema):

    algorithm: ALGORITHM_TYPE = Field(title=_('Algorithm','加密类型'))
    client_id: str = Field(title=_('Client ID','客户端id'), readonly=True, default='')
    client_secret: str = Field(title=_('Client Secret','客户端密钥'), readonly=True, default='')
    authorize: str = Field(title=_('Authorize','授权url'), readonly=True, default='')
    token: str = Field(title=_('Token','获取token地址'), readonly=True, default='')
    userinfo: str = Field(title=_('Userinfo','用户信息地址'), readonly=True, default='')
    logout: str = Field(title=_('Logout', '退出登录地址'), readonly=True, default='')
    issuer_url: str = Field(title=_('Issuer', 'Issuer'), readonly=True, default='')
