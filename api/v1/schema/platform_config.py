from ninja import Field, Schema, ModelSchema
from arkid.core.models import Platform, Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema, UserSchemaOut


class PlatformConfigIn(ModelSchema):
    class Config:
        model = Platform
        model_fields = ['is_saas', 'is_need_rent', 'frontend_url']


class PlatformConfigOut(ResponseSchema):
    data: PlatformConfigIn


class FrontendUrlSchema(Schema):    
    url:str = Field(title=_("ArkId访问地址"))
    

class FrontendUrlOut(ResponseSchema):
    data: FrontendUrlSchema