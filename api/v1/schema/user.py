from typing import List, Optional
from uuid import UUID
from ninja import ModelSchema, Schema
from arkid.core.models import User
from pydantic import Field
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema

class UserListQueryIn(Schema):
    name:str = Field(
        default=None
    )

class UserListItemOut(ModelSchema):

    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']

class UserListOut(ResponseSchema):
    data: List[UserListItemOut]

class UserCreateIn(ModelSchema):
    class Config:
        model = User
        model_fields = ['username', 'avatar']
        
class UserCreateOut(ResponseSchema):
    pass

class UserDeleteOut(ResponseSchema):
    pass

class UserItemOut(ModelSchema):
    id:UUID = Field(readonly=True)

    class Config:
        model = User
        model_fields = ['username', 'avatar']
        

class UserOut(ResponseSchema):
    data: UserItemOut

class UserUpdateIn(ModelSchema):
    class Config:
        model = User
        model_fields = ['avatar']
        
class UserUpdateOut(ResponseSchema):
    pass

class UserFieldsItemOut(Schema):
    
    id: str = Field(title=_("id"), hidden=True)
    name: str = Field(title=_("名称"))

class UserFieldsOut(ResponseSchema):
    
    data: Optional[List[UserFieldsItemOut]]