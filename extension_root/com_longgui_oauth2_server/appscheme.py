from enum import Enum
from ninja import Schema
from oauth2_provider.models import Application
from django.utils.translation import gettext_lazy as _
from typing import Optional
from pydantic import Field

class AppBaseSchema(Schema):

    type: str = Field(title=_('type', '类型'))
    logo: str = Field(title=_('logo', '图标'))
    name: str = Field(title=_('name', '名称'))
    url: str = Field(title=_('url', '主页地址'))
    description: str = Field(title=_('description', '描述'))
    data: Optional[dict] = Field(title=_('data','数据'))


class CLIENT_TYPE(str, Enum):
    confidential = _('Confidential', '私密')
    public = _('Public','公开')


class GRANT_TYPE(str, Enum):
    authorization_code = _('Authorization code', '私密')
    implicit = _('Implicit','公开')
    password = _('Resource owner password based','密码')
    client_credentials = _('Client credentials','客户端凭据')
    openid_hybrid = _('OpenID connect hybrid','OpenID链接')


class OAuth2ConfigInSchema(Schema):

    skip_authorization: bool = Field(title=_('skip authorization', '是否跳过验证'), default=False)
    redirect_uris: str = Field(title=_('redirect uris', '回调地址'))
    client_type: CLIENT_TYPE = Field(title=_('client type','客户端是否公开'))
    grant_type: GRANT_TYPE = Field(title=_('type','授权类型'))


class Oauth2ConfigOutSchema(OAuth2ConfigInSchema):

    # 输出的比输入的额外多了一些字段
    client_id: str = Field(title=_('client id','客户端id'))
    client_secret: str = Field(title=('client secret','客户端密钥'))
    authorize: str = Field(title=('authorize','授权url'))
    token: str = Field(title=('token','获取token地址'))
    userinfo: str = Field(title=('userinfo','用户信息地址'))
    logout: str = Field(title=('logout', '退出登录地址'))


class OAuth2AppSchema(AppBaseSchema):

    logo: str = Field(title=_('logo', '请选择图标'))
    url: str = Field(title=_('url', 'app url'))
    data: Oauth2ConfigOutSchema = Field(title=_('data', '数据'))


class ALGORITHM_TYPE(str, Enum):

    '' = _('No OIDC support','不支持OIDC')
    RS256 = _('RSA with SHA-2 256','RS256加密')
    HS256 = _('HMAC with SHA-2 256','HS256加密')

class OIDCConfigInSchema(OAuth2ConfigInSchema):

    algorithm = serializers.ChoiceField(choices=Application.ALGORITHM_TYPES, default=Application.NO_ALGORITHM)


class OIDCConfigOutSchema(OIDCConfigInSchema):

    # 输出的比输入的额外多了一些字段
    client_id: str = Field(title=_('client id','客户端id'))
    client_secret: str = Field(title=('client secret','客户端密钥'))
    authorize: str = Field(title=('authorize','授权url'))
    token: str = Field(title=('token','获取token地址'))
    userinfo: str = Field(title=('userinfo','用户信息地址'))
    logout: str = Field(title=('logout', '退出登录地址'))


class OIDCAppSchema(AppBaseSchema):

    logo: str = Field(title=_('logo', '请选择图标'))
    url: str = Field(title=_('url', 'app url'))
    data: OIDCConfigOutSchema = Field(title=_('data', '数据'))
