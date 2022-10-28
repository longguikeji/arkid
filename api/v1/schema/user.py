from typing import Any, List, Optional
from uuid import UUID
from ninja import ModelSchema, Schema
from arkid.core.models import User
from pydantic import Field
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema

class UserListQueryIn(Schema):
    order:str = Field(
        default=None,
        title=_("排序字段"),
        hidden=True,
        notranslation=True
    )
    username:str = Field(
        default=None,
        title=_("用户名"),
        notranslation=True
    )

    nickname:str = Field(
        default=None,
        title=_("昵称"),
    )

    mobile:str = Field(
        default=None,
        title=_("电话"),
    )

    email:str = Field(
        default=None,
        title=_("邮箱"),
    )

class UserListItemOut(ModelSchema):

    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar','created']
        
    created:Any = Field(
        title=_("注册时间")
    )
    
class UserListOut(ResponseSchema):
    data: List[UserListItemOut]


class UserPullItemOut(ModelSchema):

    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar','is_platform_user','is_del','is_active','created','updated']
        
    created:Any = Field(
        title=_("注册时间")
    )
    
class UserPullOut(ResponseSchema):
    data: List[UserPullItemOut]

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
    name: str = Field(title=_("名称"), notranslation=True)

class UserFieldsOut(ResponseSchema):
    
    data: Optional[List[UserFieldsItemOut]]