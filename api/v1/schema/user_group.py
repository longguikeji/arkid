from typing import List
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from requests import Response
from arkid.core.models import User, UserGroup
from arkid.core.schema import ResponseSchema
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _

select_usergroup_parent_page = pages.TablePage(select=True,name=_("选择上级分组"))

pages.register_front_pages(select_usergroup_parent_page)

select_usergroup_parent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET
    )
)

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

    parent_id: str = Field(
        field="id",
        page=select_usergroup_parent_page,
        link="parent_id"
    )

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
        model_fields = ['id', 'name',"parent"]

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
