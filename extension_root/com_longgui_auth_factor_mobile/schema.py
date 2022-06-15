from typing import Optional
from ninja import Field, ModelSchema, Schema
from arkid.core.actions import DirectAction
from arkid.core.schema import ResponseSchema
from .models import UserMobile
    
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