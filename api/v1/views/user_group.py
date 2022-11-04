
from ninja import Field
from ninja import Schema,Query
from ninja import ModelSchema
from arkid.core.api import api, operation
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.models import UserGroup, User
from django.shortcuts import get_list_or_404, get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import (
    CREATE_GROUP, UPDATE_GROUP, DELETE_GROUP,
    GROUP_ADD_USER, GROUP_REMOVE_USER,
)
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from uuid import UUID

from api.v1.schema.user_group import *
from arkid.core.pagenation import CustomPagination


class UserGroupPermissionListSelectSchemaOut(Schema):

    id: UUID = Field(default=None)
    in_current: bool
    name: str

@transaction.atomic
@api.post("/tenant/{tenant_id}/user_groups/", response=UserGroupCreateOut, tags=['用户分组'])
@operation(UserGroupCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_group(request, tenant_id: str, data: UserGroupCreateIn):
    '''
    分组创建
    '''
    data_dict = data.dict()
    group = UserGroup()

    group.tenant_id = tenant_id
    group.name = data_dict.pop('name', '')
    parent = data_dict.pop("parent",None)
    parent_id = parent.get("id",None) if parent else None
    group.parent = get_object_or_404(UserGroup, id=parent_id) if parent_id else None
    group.save()
    # 需要注意额外的字段
    for key,value in data_dict.items():
        if value:
            setattr(group,key,value)
    group.save()
    # 分发事件开始
    result = dispatch_event(
        Event(
            tag=CREATE_GROUP, 
            tenant=request.tenant, 
            request=request,
            data=group
        )
    )
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/user_groups/", response=UserGroupListOut, tags=['用户分组'])
@operation(UserGroupListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def list_groups(request, tenant_id: str,  parent_id: str = None):
    '''
    分组列表
    '''
    from arkid.core.perm.permission_data import PermissionData
    usergroups = UserGroup.valid_objects.filter(
        tenant_id=tenant_id,
        parent__id=parent_id
    )
    login_user = request.user
    tenant = request.tenant
    pd = PermissionData()
    usergroups = pd.get_manage_user_group(login_user, tenant, usergroups)
    return {"data": list(usergroups.all())}


@api.get("/tenant/{tenant_id}/user_groups/pull/", response=List[UserGroupPullItemOut], tags=['用户分组'])
@operation(UserGroupPullOut, roles=[PLATFORM_ADMIN])
@paginate(CustomPagination)
def user_group_pull(request, tenant_id: str,  parent_id: str = ''):
    '''
    拉取用户分组
    '''
    usergroups = UserGroup.objects.filter(
        tenant_id=tenant_id,
    )
    if parent_id != '':
        usergroups = usergroups.filter(parent__id=parent_id)
    usergroups = usergroups.order_by('created')
    return usergroups


@api.get("/tenant/{tenant_id}/user_groups/{id}/", response=UserGroupDetailOut, tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_group(request, tenant_id: str, id: str):
    '''
    获取分组
    '''
    group = get_object_or_404(UserGroup.expand_objects, id=id, is_del=False)
    group["parent"] = UserGroup.active_objects.get(id=group["parent_id"]) if group["parent_id"] else None
    return {
        "data": group
    }


@api.post("/tenant/{tenant_id}/user_groups/{id}/", tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_group(request, tenant_id: str, id: str, data: UserGroupUpdateIn):
    '''
    修改分组
    '''
    data_dict = data.dict()
    group = get_object_or_404(UserGroup.active_objects, id=id)
    group.name = data_dict.pop("name",None)
    parent = data_dict.pop("parent",None)
    parent_id = parent.get("id",None) if parent else None
    group.parent = get_object_or_404(UserGroup.active_objects, id=parent_id) if parent_id else None
    
    if group.parent == group:
        return ErrorDict(ErrorCode.USER_GROUP_PARENT_CANT_BE_ITSELF)
    group.save()
    # 需要注意额外的字段
    for key,value in data_dict.items():
        if value:
            setattr(group,key,value)
    group.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_GROUP, tenant=request.tenant,
                   request=request, data=group))
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)


@api.delete("/tenant/{tenant_id}/user_groups/{id}/", response=UserGroupDeleteOut, tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_group(request, tenant_id: str, id: str):
    '''
    删除分组
    '''
    group = get_object_or_404(UserGroup.valid_objects, id=id)
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_GROUP, tenant=request.tenant,
                   request=request, data=group))
    # 分发事件结束
    group.delete()
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/users/", response=List[UserGroupUserListItemOut], tags=['用户分组'])
@operation(UserGroupUserListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_group_users(request, tenant_id: str, user_group_id: str):
    '''
    获取分组用户
    '''
    group = get_object_or_404(UserGroup.valid_objects, id=user_group_id)
    users = User.expand_objects.filter(id__in=group.users.all()).all()
    return users


@api.post("/tenant/{tenant_id}/user_groups/{user_group_id}/users/", tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_users_add(request, tenant_id: str, user_group_id: str, data: UserGroupUserIn):
    '''
    分组添加用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup, id=user_group_id, is_del=False)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.add(user)
        group.save()
        # 分发事件开始
        result = dispatch_event(Event(tag=GROUP_ADD_USER, tenant=request.tenant, request=request, data=group))
        # 分发事件结束
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/user_groups/{user_group_id}/batch_users/", tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_batch_users_remove(request, tenant_id: str, user_group_id: str, data: UserGroupUserIn):
    '''
    分组批量移除用户
    '''
    user_ids = data.user_ids
    group = get_object_or_404(UserGroup.active_objects, id=user_group_id)
    if user_ids:
        users = User.active_objects.filter(id__in=user_ids)
        for user in users:
            group.users.remove(user)
        group.save()
        # 分发事件开始
        result = dispatch_event(Event(tag=GROUP_REMOVE_USER, tenant=request.tenant, request=request, data=group))
        # 分发事件结束
    return ErrorDict(ErrorCode.OK)


@api.delete("/tenant/{tenant_id}/user_groups/{user_group_id}/users/{id}/", tags=['用户分组'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def group_users_remove(request, tenant_id: str, user_group_id: str, id: str):
    '''
    分组移除用户
    '''
    group = get_object_or_404(UserGroup.active_objects, id=user_group_id)
    user = User.active_objects.filter(id=id).first()
    if user:
        group.users.remove(user)
    group.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=GROUP_REMOVE_USER, tenant=request.tenant, request=request, data=group))
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)



@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/exclude_users/", response=List[UserGroupExcludeUsersItemOut], tags=["用户分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_exclude_users(request, tenant_id: str, user_group_id: str,query_data:UserGroupExcludeUsersFilter=Query(...)):
    """ 获取所有未添加到分组的用户
    """
    tenant = request.tenant
    users = tenant.user_set
    group = get_object_or_404(UserGroup.active_objects, id=user_group_id)
    group_users = group.users.all()
    super_user_id = User.valid_objects.order_by('created').first().id
    users = users.exclude(id__in=group_users).exclude(id=super_user_id).all()
    if query_data.username:
        users = User.expand_objects.filter(id__in=users,username__contains=query_data.username).all()
    else:
        users = User.expand_objects.filter(id__in=users).all()
    return users

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/all_permissions/", response=List[UserGroupPermissionListSelectSchemaOut], tags=["用户分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_user_group_all_permissions(request, tenant_id: str, user_group_id:str):
    """ 获取所有权限并附带是否已授权给用户分组状态
    """
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_user_group_all_permissions(tenant_id, user_group_id)
