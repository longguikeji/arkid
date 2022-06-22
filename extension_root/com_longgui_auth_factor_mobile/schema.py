from typing import Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from arkid.core.actions import DirectAction
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
    



class MobileAuthFactorConfigSchema(Schema):
    
    id:UUID = Field(
        hidden=True,
    )
    
    name:str
    
    package:str

class SendSMSCodeIn(Schema):
    areacode:Optional[str] = Field(
        title=_("区号"),
        default="86"
    )
    
    mobile:str = Field(
        title=_("电话号码")
    )
class SendSMSCodeOut(ResponseSchema):
    pass