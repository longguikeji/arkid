from enum import Enum
from ninja import Schema
from arkid.core.translation import gettext_default as _
from typing import Optional
from pydantic import Field

class CasConfigSchema(Schema):

    # 输出的比输入的额外多了一些字段
    login: str = Field(title=_('Login','登录地址'), readonly=True, default='')
    # logout: str = Field(title=_('logout','退出登录地址'), readonly=True, default='')
    logout: str = Field(title=_('Logout','登出地址'), readonly=True, default='')
    service_validate: str = Field(title=_('Service Validate','服务校验地址'), readonly=True, default='')
    proxy_validate: str = Field(title=_('Proxy Validate','代理验证地址'), readonly=True, default='')
    proxy: str = Field(title=_('Proxy','代理地址'), readonly=True, default='')
    p3_service_validate: str = Field(title=_('P3 Service Validate','p3服务验证地址'), readonly=True, default='')
    p3_proxy_validate: str = Field(title=_('P3 Proxy Validate','p3代理校验地址'), readonly=True, default='')
    warn: str = Field(title=_('Warn','警告地址'), readonly=True, default='')
    saml_validate: str = Field(title=_('Saml Validate','saml服务验证地址'), readonly=True, default='')
