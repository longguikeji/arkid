from ninja import Field, Schema, ModelSchema
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema, UserSchemaOut


class PlatformConfigIn(Schema):
    
    multi_tenant_switch: bool = Field(
        title=_("租户开关")
    )
        
class PlatformConfigItemOut(Schema):
    
    multi_tenant_switch: bool = Field(
        title=_("租户开关")
    )        

class PlatformConfigOut(ResponseSchema):
    data: PlatformConfigItemOut
