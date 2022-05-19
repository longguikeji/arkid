
from ninja import Schema
from ninja import Field
from ninja import ModelSchema
from arkid.core.api import api, operation
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.models import Permission, SystemPermission
from django.shortcuts import get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from uuid import UUID

import uuid


class PermissionListSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category', 'is_system']


class PermissionSchemaOut(Schema):
    permission_id: str


class PermissionSchemaIn(ModelSchema):

    app_id: str

    class Config:
        model = Permission
        model_fields = ['name', 'category']


class PermissionEditSchemaIn(ModelSchema):

    class Config:
        model = Permission
        model_fields = ['name', 'category']


class PermissionDetailSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)
    parent_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category']


class PermissionStrSchemaOut(Schema):
    result: str

@transaction.atomic
@api.post("/tenant/{tenant_id}/permissions", response=PermissionSchemaOut, tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission(request, tenant_id: str, data: PermissionSchemaIn):
    '''
    权限创建
    '''
    permission = Permission()
    permission.tenant_id = tenant_id
    permission.name = data.name
    permission.category = data.category
    permission.code = 'other_{}'.format(uuid.uuid4())
    permission.parent = None
    permission.app_id = data.app_id
    permission.is_system = False
    permission.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=CREATE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {"permission_id": permission.id.hex}


@api.get("/tenant/{tenant_id}/permissions", response=List[PermissionListSchemaOut], tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate
def list_permissions(request, tenant_id: str,  app_id: str = None, user_id: str = None, group_id: str = None):
    '''
    权限列表
    '''
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_permissions_by_search(tenant_id, app_id, user_id, group_id)


@api.get("/tenant/{tenant_id}/permission/{permission_id}", response=PermissionDetailSchemaOut, tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission(request, tenant_id: str, permission_id: str):
    '''
    获取权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    return permission


@api.put("/tenant/{tenant_id}/permission/{permission_id}", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permission(request, tenant_id: str, permission_id: str, data: PermissionEditSchemaIn):
    '''
    修改权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    permission.name = data.name
    permission.category = data.category
    permission.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/permission/{permission_id}", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission(request, tenant_id: str, permission_id: str):
    '''
    删除权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    permission.delete()
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}


@api.get("/tenant/{tenant_id}/permissionstr", tags=['权限'], response=PermissionStrSchemaOut, auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_str(request, tenant_id: str,  app_id: str = None):
    '''
    权限结果
    '''
    from arkid.core.models import User
    # user = request.user
    user, _ = User.objects.get_or_create(
        username="hanbin",
    )
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_permission_str(user, tenant_id, app_id)