from uuid import UUID
from typing import List
from ninja import Field
from ninja import Schema
from ninja import ModelSchema
from arkid.core.models import User, UserGroup
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _
from api.v1.pages.tenant_manage.child_manager import select_user_page, select_permission_page, select_scope_page

class ChildManagerListOut(ModelSchema):

    class Config:
        model = User
        model_fields = ["id","username"]

    groups: str = Field(title=_('Group', '所属分组'))

    @staticmethod
    def resolve_groups(obj):
        usergroups = UserGroup.valid_objects.filter(
            users=obj
        )
        usergroup_str = ''
        for index, usergroup in enumerate(usergroups):
            usergroup_str = usergroup_str + usergroup.name
            if index < (len(usergroups)-1):
                usergroup_str = usergroup_str + ','
        return usergroup_str


class ChildManagerDeatilOut(Schema):

    permissions: List[UUID] = Field(
        field="id",
        page=select_permission_page.tag,
        link="name",
        default=None,
        title=_("拥有权限")
    )

    manager_scope: List[UUID] = Field(
        field="id",
        page=select_scope_page.tag,
        link="name",
        default=None,
        title=_("管理范围")
    )

class ChildManagerCreateSchemaIn(Schema):

    users: List[UUID] = Field(
        field="id",
        page=select_user_page.tag,
        link="name",
        default=None,
        title=_("选择用户")
    )

    permissions: List[UUID] = Field(
        field="id",
        page=select_permission_page.tag,
        link="name",
        default=None,
        title=_("拥有权限")
    )

    manager_scope: List[UUID] = Field(
        field="id",
        page=select_scope_page.tag,
        link="name",
        default=None,
        title=_("管理范围")
    )