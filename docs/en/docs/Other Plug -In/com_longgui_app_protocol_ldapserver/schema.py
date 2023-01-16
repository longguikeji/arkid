from typing import List, Optional
from uuid import UUID
from ninja import Field, Schema
from arkid.core.extension import create_extension_schema
from arkid.core.models import Tenant
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

class LDAPServerConfigSchema(Schema):

    BASE_DN:str = Field(
        default="dc=longguikeji, dc=com"
    )
    
class LDAPApplicationSettingsSchema(Schema):
    
    server:Optional[LDAPServerConfigSchema] = Field(
        title=_("LDAP服务配置")
    )
    
class LDAPServerLoginBaseIn(Schema):
    
    username:str = Field(
        title=_("用户名")
    )
    
    password:str = Field(
        title=_("密码")
    )
    
    basedn:str = Field(
        title=_("BASEDN")
    )
    
LDAPServerLoginOut = create_extension_schema(
    "LDAPServerLoginOut",
    __file__,
    [
        (
            "token",
            str,
            Field(
                title=_("token")
            )
        )
    ],
    base_schema=ResponseSchema
)
    
LDAPServerLoginIn = create_extension_schema(
    "LDAPServerLoginIn",
    __file__,
    base_schema=LDAPServerLoginBaseIn
)

class LDAPServerDataSearchBaseIn(Schema):
    
    dn:str = Field(
        title=_("DOMAIN_NAME")
    )
    
    scope:str = Field(
        title=_("SCOPE")
    )
    
    attributes:list = Field(
        title=_("ATTRIBUTES")
    )
    
    type:str
    
class LDAPServerDataSearchItemOut(Schema):
    
    dn:Optional[str]        
    
    attributes:dict
    
class LDAPServerDataSearchBaseOut(ResponseSchema):
    data:Optional[List[LDAPServerDataSearchItemOut]]
    
LDAPServerDataSearchOut = create_extension_schema(
    "LDAPServerDataSearchOut",
    __file__,
    base_schema=LDAPServerDataSearchBaseOut
)
    
LDAPServerDataSearchIn = create_extension_schema(
    "LDAPServerDataSearchIn",
    __file__,
    base_schema=LDAPServerDataSearchBaseIn
)

class LDAPServerSettngsItemOut(Schema):
    ARKID_DOMAIN:str = Field(
        readonly=True,
        default=""
    )

    BASE_DN:str = Field(
        readonly=True,
        default="dc=longguikeji, dc=com"
    )
    
    LOGIN_USERNAME_FORMAT:str = Field(
        readonly=True,
        default="",
        title=_("登录名")
    )
    
class LDAPServerSettingsBaseOut(ResponseSchema):
    data:Optional[LDAPServerSettngsItemOut]
    
LDAPServerSettingsOut = create_extension_schema(
    "LDAPServerSettingsOut",
    __file__,
    base_schema=LDAPServerSettingsBaseOut
)

UserFieldsOut = create_extension_schema(
    "UserFieldsOut",
    __file__,
    [
        (
            "data",
            List[str],
            Field(
                title=_("字段名")
            )
        )
    ],
    ResponseSchema
)

GroupFieldsOut = create_extension_schema(
    "GroupFieldsOut",
    __file__,
    [
        (
            "data",
            List[str],
            Field(
                title=_("字段名")
            )
        )
    ],
    ResponseSchema
)

class LDAPTenantItemOut(Schema):
    id:str
    name:str
    slug:str

class LDAPSearchTenantOut(ResponseSchema):
    data: Optional[List[LDAPTenantItemOut]] = []
    
class LDAPSearchTenantUserOut(ResponseSchema):
    data: Optional[List] = []
    
class LDAPFindTenantOut(ResponseSchema):
    pass