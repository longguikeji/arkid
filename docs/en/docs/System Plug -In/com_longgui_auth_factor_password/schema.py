from typing import Optional
from ninja import Field, ModelSchema, Schema
from arkid.core.schema import ResponseSchema
from .models import UserPassword
    
class UpdateMinePasswordIn(Schema):
    
    old_password:Optional[str] = Field(
        type="password",
        title="原密码",
        default=None
    )
    
    password:str = Field(
        type="password",
        title="新密码",
    )
    
    confirm_password:str = Field(
        type="password",
        title="确认密码",
        default=""
    )
    
class UpdateMinePasswordOut(ResponseSchema):
    pass