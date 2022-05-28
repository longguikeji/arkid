from ninja import Field, ModelSchema, Schema
from arkid.core.schema import ResponseSchema
from .models import UserPassword

class MinePasswordItemOut(Schema):
    
    password:str = Field(
        type="password",
        title="确认密码",
    )
    
    confirm_password:str = Field(
        type="password",
        title="确认密码",
        default=""
    )

class MinePasswordOut(ResponseSchema):
    
    data:MinePasswordItemOut
    
class UpdateMinePasswordIn(Schema):
    password:str = Field(
        type="password",
        title="确认密码",
    )
    
    confirm_password:str = Field(
        type="password",
        title="确认密码",
        default=""
    )
    
class UpdateMinePasswordOut(ResponseSchema):
    pass