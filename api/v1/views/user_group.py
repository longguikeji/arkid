
from ninja import Schema
from ninja import ModelSchema
from arkid.core.api import api, operation
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.models import UserGroup, User
from django.shortcuts import get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import CREATE_GROUP, UPDATE_GROUP, DELETE_GROUP
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from uuid import UUID

from api.v1.schema.user_group import UserGroupDeleteOut, UserGroupDetailOut, UserGroupIn, UserGroupItemOut, UserGroupListItemOut, UserGroupListOut, UserGroupOut, UserGroupUserIn, UserGroupUserListItemOut, UserGroupUserListOut, UserGroupUserOut
from arkid.core.pagenation import CustomPagination


@transaction.atomic
@api.post("/tenant/{tenant_id}/user_groups/", response=UserGroupOut, tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_group(request, tenant_id: str, data: UserGroupIn):
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
    return {"data":{"id": group.id.hex}}


@api.get("/tenant/{tenant_id}/user_groups/", response=UserGroupListOut, tags=['用户分组'], auth=None)
@operation(UserGroupListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def list_groups(request, tenant_id: str,  parent_id: str = None):
    '''
    分组列表
    '''
    usergroups = UserGroup.valid_objects.filter(
        tenant_id=tenant_id
    )
    if parent_id:
        usergroups = usergroups.filter(parent_id=parent_id)
    return {"data": list(usergroups.all())}


@api.get("/tenant/{tenant_id}/user_groups/{id}/", response=UserGroupDetailOut, tags=['用户分组'], auth=None)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_group(request, tenant_id: str, id: str):
    '''
    获取分组
    '''
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    return {"data":group}


@api.post("/tenant/{tenant_id}/user_groups/{id}/", tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_group(request, tenant_id: str, id: str, data: UserGroupIn):
    '''
    修改分组
    '''
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    group.name = data.name
    if data.parent_id:
        group.parent_id = data.parent_id
    group.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_GROUP, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/user_groups/{id}/",response=UserGroupDeleteOut,tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_group(request, tenant_id: str, id: str):
    '''
    删除分组
    '''
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_GROUP, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    group.delete()
    return {'error': ErrorCode.OK.value}


@api.get("/tenant/{tenant_id}/user_groups/{id}/users/", response=List[UserGroupUserListItemOut], tags=['用户分组'], auth=None)
@operation(UserGroupUserListOut,roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_group_users(request, tenant_id: str, id: str):
    '''
    获取分组用户
    '''
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    return group.users.all()


@api.post("/tenant/{tenant_id}/user_groups/{id}/users/", tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_users_add(request, tenant_id: str, id: str, data:UserGroupUserIn):
    '''
    分组添加用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.add(user)
        group.save()
    return {'error': ErrorCode.OK.value}


@api.put("/tenant/{tenant_id}/user_groups/{id}/users/", tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_batch_users_remove(request, tenant_id: str, id: str, data:UserGroupUserIn):
    '''
    分组批量移除用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.remove(user)
        group.save()
    return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/user_groups/{id}/users/{user_id}/", tags=['用户分组'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_users_remove(request, tenant_id: str, id: str, user_id: str):
    '''
    分组移除用户
    '''
    group = get_object_or_404(UserGroup, id=id, is_del=False)
    user = User.active_objects.filter(id=user_id).first()
    if user:
        group.users.remove(user)
    group.save()
    return {'error': ErrorCode.OK.value}

# @api.get("/tenant/{tenant_id}/user_groups/{user_id}/select_users/", tags=["用户分组"],auth=None)
# def get_select_users(request, tenant_id: str, user_id: str):
#     """ 获取所有用户并附加是否在当前分组的状态,TODO
#     """
#     return {}
# @api.get("/tenant/{tenant_id}/user_groups/{user_id}/all_permissions/",tags=["用户分组"],auth=None)
# def get_user_group_all_permissions(request, tenant_id: str,user_id:str):
#     """ 获取所有权限并附带是否已授权给用户分组状态,TODO
#     """
#     return []