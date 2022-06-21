from typing import Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from arkid.core.actions import DirectAction
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

    
class UpdateMineMobileIn(Schema):
        
    modile:str = Field(
        title='手机号',
        suffix_action=DirectAction(
            name='发送验证码',
            path='',
            method='',
            delay=60,
        ).dict()
    )
    
    code:str = Field(title='验证码')
    
class UpdateMineMobileOut(ResponseSchema):
    pass


class MobileAuthFactorConfigSchema(Schema):
    
    id:UUID = Field(
        hidden=True,
    )
    
    name:str

class SendSMSCodeIn(Schema):
    config_id:str = Field(
        title=_("配置ID")
    )
    
    areacode:Optional[str] = Field(
        title=_("区号"),
        default="86"
    )
    
    phone_number:str = Field(
        title=_("电话号码")
    )
    package:str = Field(
        title=_("包名")
    )
    
class SendSMSCodeOut(ResponseSchema):
    pass