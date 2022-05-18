from typing import List
from uuid import UUID
from ninja import ModelSchema, Schema
from requests import Response
from arkid.core.models import User, UserGroup
from arkid.core.schema import ResponseSchema


class UserGroupListItemOut(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']

class UserGroupListOut(ResponseSchema):

    data: List[UserGroupListItemOut]


class UserGroupItemOut(ModelSchema):

    parent_id: str

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']

class UserGroupOut(ResponseSchema):
    data: UserGroupItemOut

class UserGroupIn(ModelSchema):

    parent_id: str = None

    class Config:
        model = UserGroup
        model_fields = ['name']

class UserGroupDeleteOut(ResponseSchema):
    pass

class UserGroupUserListItemOut(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username']

class UserGroupUserListOut(ResponseSchema):
    data:List[UserGroupUserListItemOut]


class UserGroupDetailItemOut(ModelSchema):

    parent_id: UUID = None

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']

class UserGroupDetailOut(ResponseSchema):
    data:UserGroupDetailItemOut


class UsersOut(ModelSchema):

    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']


class UserGroupUserOut(ModelSchema):
    users: List[UsersOut]

    class Config:
        model = UserGroup
        model_fields = ['users']


class UserGroupUserIn(Schema):
    user_ids: List[str]
