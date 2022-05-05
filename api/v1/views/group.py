
from ninja import Schema
from ninja import ModelSchema
from arkid.core.api import api
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.models import UserGroup, User
from django.shortcuts import get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import CREATE_GROUP, UPDATE_GROUP, DELETE_GROUP
from uuid import UUID


class UserGroupListSchemaOut(ModelSchema):

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']


class UserGroupSchemaOut(Schema):
    group_id: str


class UserGroupSchemaIn(ModelSchema):

    parent_id: str = None

    class Config:
        model = UserGroup
        model_fields = ['name']


class UserGroupDetailSchemaOut(ModelSchema):

    parent_id: UUID = None

    class Config:
        model = UserGroup
        model_fields = ['id', 'name']


class UsersSchemaOut(ModelSchema):

    class Config:
        model = User
        model_fields = ['id', 'username', 'avatar']


class UserGroupUserSchemaOut(ModelSchema):
    users: List[UsersSchemaOut]

    class Config:
        model = UserGroup
        model_fields = ['users']


class UserGroupUserSchemaIn(Schema):
    user_ids: List[str]


@transaction.atomic
@api.post("/{tenant_id}/groups", response=UserGroupSchemaOut, tags=['分组'], auth=None)
def create_group(request, tenant_id: str, data: UserGroupSchemaIn):
    '''
    分组创建
    '''
    group = UserGroup()
    group.tenant_id = tenant_id
    group.name = data.name
    if data.parent_id:
        group.parent_id = data.parent_id
    group.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=CREATE_GROUP, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    return {"group_id": group.id.hex}


@api.get("/{tenant_id}/groups", response=List[UserGroupListSchemaOut], tags=['分组'], auth=None)
@paginate
def list_groups(request, tenant_id: str,  parent_id: str = None):
    '''
    分组列表
    '''
    usergroups = UserGroup.valid_objects.filter(
        tenant_id=tenant_id
    )
    if parent_id:
        usergroups = usergroups.filter(parent_id=parent_id)
    return usergroups


@api.get("/{tenant_id}/groups/{group_id}", response=UserGroupDetailSchemaOut, tags=['分组'], auth=None)
def get_group(request, tenant_id: str, group_id: str):
    '''
    获取分组
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    return group


@api.put("/{tenant_id}/groups/{group_id}", tags=['分组'], auth=None)
def update_group(request, tenant_id: str, group_id: str, data: UserGroupSchemaIn):
    '''
    修改分组
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    group.name = data.name
    if data.parent_id:
        group.parent_id = data.parent_id
    group.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_GROUP, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}


@api.delete("/{tenant_id}/groups/{group_id}", tags=['分组'], auth=None)
def delete_group(request, tenant_id: str, group_id: str):
    '''
    删除分组
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_GROUP, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    group.delete()
    return {'error': ErrorCode.OK.value}


@api.get("/{tenant_id}/groups/{group_id}/users", response=UserGroupUserSchemaOut, tags=['分组'], auth=None)
def get_group_users(request, tenant_id: str, group_id: str):
    '''
    获取分组用户
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    return group


@api.post("/{tenant_id}/groups/{group_id}/users", tags=['分组'], auth=None)
def group_users_add(request, tenant_id: str, group_id: str, data:UserGroupUserSchemaIn):
    '''
    分组添加用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.add(user)
        group.save()
    return {'error': ErrorCode.OK.value}


@api.put("/{tenant_id}/groups/{group_id}/users", tags=['分组'], auth=None)
def group_users_remove(request, tenant_id: str, group_id: str, data:UserGroupUserSchemaIn):
    '''
    分组批量移除用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.remove(user)
        group.save()
    return {'error': ErrorCode.OK.value}


@api.delete("/{tenant_id}/groups/{group_id}/users/{user_id}", tags=['分组'], auth=None)
def group_users_remove(request, tenant_id: str, group_id: str, user_id: str):
    '''
    分组移除用户
    '''
    group = get_object_or_404(UserGroup, id=group_id, is_del=False)
    user = User.active_objects.filter(id=user_id).first()
    if user:
        group.users.remove(user)
    group.save()
    return {'error': ErrorCode.OK.value}