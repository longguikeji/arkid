from typing import List
from ninja import Schema
from ninja import ModelSchema
from arkid.core.api import api
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.models import UserGroup
from django.shortcuts import get_object_or_404


class UserGroupListSchemaOut(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']


class UserGroupSchemaOut(Schema):
    group_id: str


class UserGroupSchemaIn(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['name']


class UserGroupDetailSchemaOut(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']


@transaction.atomic
@api.post("/{tenant_id}/groups", response=UserGroupSchemaOut, tags=['分组'], auth=None)
def create_group(request, tenant_id: str, data: UserGroupSchemaIn):
    '''
    分组创建
    '''
    group = UserGroup()
    group.tenant_id = tenant_id
    group.name = data.name
    group.save()
    return {"group_id": group.id.hex}


@api.get("/{tenant_id}/groups", response=List[UserGroupListSchemaOut], tags=['分组'], auth=None)
@paginate
def list_groups(request, tenant_id: str):
    '''
    分组列表
    '''
    usergroups = UserGroup.valid_objects.filter(
        tenant_id=tenant_id
    )
    return usergroups


@api.get("/{tenant_id}/groups/{group_id}", response=UserGroupDetailSchemaOut, tags=['分组'], auth=None)
def get_group(request, tenant_id: str, group_id: str):
    '''
    获取分组
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    return group


@api.delete("/{tenant_id}/groups/{group_id}", tags=['分组'], auth=None)
def delete_group(request, tenant_id: str, group_id: str):
    '''
    删除分组
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    # 分发事件开始
    # 分发事件结束
    group.delete()
    return {'error': ErrorCode.OK.value}
