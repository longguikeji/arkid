from typing import List, Optional
from ninja import Field, Schema, ModelSchema
from arkid.core.models import Platform, Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema, UserSchemaOut


class PlatformConfigIn(ModelSchema):
    class Config:
        model = Platform
        model_fields = ['is_saas', 'is_need_rent']


class PlatformConfigOut(ResponseSchema):
    data: PlatformConfigIn


class FrontendUrlSchemaIn(Schema):    
    url: str = Field(title=_("DB URL", "数据库前端地址"))


class FrontendUrlSchema(Schema):    
    db_url: Optional[str] = Field(title=_("DB URL", "数据库前端地址"))
    toml_url: str = Field(title=_("TOML URL", "配置文件前端地址"))
    dev: bool = Field(title=_("DEV ENVIRONMENT", "是否为开发环境"))
    

class FrontendUrlOut(ResponseSchema):
    data: Optional[FrontendUrlSchema]