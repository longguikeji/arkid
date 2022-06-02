from typing import List, Optional
from uuid import UUID
from ninja import Field, ModelSchema, Schema
from requests import Response
from arkid.core.models import User, UserGroup
from arkid.core.schema import ResponseSchema
from arkid.core import pages,actions
from arkid.core.translation import gettext_default as _

select_usergroup_parent_page = pages.TreePage(select=True,name=_("选择上级分组"))

pages.register_front_pages(select_usergroup_parent_page)

select_usergroup_parent_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/app_groups/?parent_id={id}',
            method=actions.FrontActionMethod.GET
        )
    ],
)

class UserGroupListItemOut(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']

class UserGroupListOut(ResponseSchema):

    data: List[UserGroupListItemOut]

class UserGroupCreateOut(ResponseSchema):
    pass

class UserGroupCreateIn(ModelSchema):

    parent: Optional[str] = Field(
        title=_("上级用户分组"),
        field="id",
        page=select_usergroup_parent_page.tag,
        link="name"
    )

    class Config:
        model = UserGroup
        model_fields = ['name']
        
class UserGroupUpdateOut(ResponseSchema):
    pass

class UserGroupUpdateIn(ModelSchema):

    parent: Optional[str] = Field(
        title=_("上级用户分组"),
        field="id",
        page=select_usergroup_parent_page.tag,
        link="name"
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


class UserGroupDetailItemOut(Schema):
    id: UUID =Field(
        readonly=True,
        hidden=False
    )
    
    name:str = Field(
        title=_("分组名称")
    )
    
    parent:Optional[UUID] = Field(
        field="id",
        page=select_usergroup_parent_page.tag,
        link="name",
        title=_("上级应用分组"),
        show="parent_name"
    )
    
    parent_name: Optional[str] = Field(
        title=_("上级应用分组名称"),
        hidden=True,
        readonly=True
    )
    
class UserGroupDetailOut(ResponseSchema):
    data:UserGroupDetailItemOut


class UserGroupUserListItemOut(ModelSchema):
    
    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']


class UserGroupUserListOut(ResponseSchema):
    users: List[UserGroupUserListItemOut]


class UserGroupUserIn(Schema):
    user_ids: List[str]

class UserGroupExcludeUsersItemOut(Schema):

    id: UUID = Field(default=None)
    username: str
    avatar: str
