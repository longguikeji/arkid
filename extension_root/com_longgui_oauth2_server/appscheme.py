from enum import Enum
from ninja import Schema
from oauth2_provider.models import Application
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field


class CLIENT_TYPE(str, Enum):
    confidential = _('Confidential', '私密')
    public = _('Public','公开')


class GRANT_TYPE(str, Enum):
    authorization_code = _('Authorization code', '私密')
    implicit = _('Implicit','公开')
    password = _('Resource owner password based','密码')
    client_credentials = _('Client credentials','客户端凭据')
    openid_hybrid = _('OpenID connect hybrid','OpenID链接')


class ConfigBaseSchema(Schema):

    skip_authorization: bool = Field(title=_('skip authorization', '是否跳过验证'), default=False)
    redirect_uris: str = Field(title=_('redirect uris', '回调地址'))
    client_type: CLIENT_TYPE = Field(title=_('client type','客户端是否公开'))
    grant_type: GRANT_TYPE = Field(title=_('type','授权类型'))


class Oauth2ConfigSchema(ConfigBaseSchema):

    # 输出的比输入的额外多了一些字段
    client_id: str = Field(title=_('client id','客户端id'), readonly=True)
    client_secret: str = Field(title=_('client secret','客户端密钥'), readonly=True)
    authorize: str = Field(title=_('authorize','授权url'), readonly=True)
    token: str = Field(title=_('token','获取token地址'), readonly=True)
    userinfo: str = Field(title=_('userinfo','用户信息地址'), readonly=True)
    logout: str = Field(title=_('logout', '退出登录地址'), readonly=True)


# class OAuth2AppSchema(AppBaseSchema):

#     data: Oauth2ConfigSchema = Field(title=_('data', '数据'))


class ALGORITHM_TYPE(str, Enum):

    RS256 = _('RSA with SHA-2 256','RS256加密')
    HS256 = _('HMAC with SHA-2 256','HS256加密')


class OIDCConfigSchema(ConfigBaseSchema):

    algorithm: ALGORITHM_TYPE = Field(title=_('algorithm','加密类型'))
    client_id: str = Field(title=_('client id','客户端id'), readonly=True)
    client_secret: str = Field(title=_('client secret','客户端密钥'), readonly=True)
    authorize: str = Field(title=_('authorize','授权url'), readonly=True)
    token: str = Field(title=_('token','获取token地址'), readonly=True)
    userinfo: str = Field(title=_('userinfo','用户信息地址'), readonly=True)
    logout: str = Field(title=_('logout', '退出登录地址'), readonly=True)


# class OIDCAppSchema(AppBaseSchema):

#     data: OIDCConfigSchema = Field(title=_('data', '数据'))
