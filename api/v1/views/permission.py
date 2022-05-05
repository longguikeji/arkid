
from ninja import Schema
from ninja import Field
from ninja import ModelSchema
from arkid.core.api import api
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.models import Permission
from django.shortcuts import get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION
from uuid import UUID

import uuid


class PermissionListSchemaOut(ModelSchema):

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category', 'is_system']


class PermissionSchemaOut(Schema):
    permission_id: str


class PermissionSchemaIn(ModelSchema):

    app_id: str = None
    parent_id: str = None

    class Config:
        model = Permission
        model_fields = ['name', 'category']


class PermissionDetailSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)
    parent_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category']


@transaction.atomic
@api.post("/{tenant_id}/permissions", response=PermissionSchemaOut, tags=['权限'], auth=None)
def create_permission(request, tenant_id: str, data: PermissionSchemaIn):
    '''
    权限创建
    '''
    permission = Permission()
    permission.tenant_id = tenant_id
    permission.name = data.name
    permission.category = data.category
    permission.code = 'other_{}'.format(uuid.uuid4())
    if data.parent_id:
        permission.parent_id = data.parent_id
    if data.app_id:
        permission.app_id = data.app_id
    permission.is_system = False
    permission.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=CREATE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {"permission_id": permission.id.hex}


@api.get("/{tenant_id}/permissions", response=List[PermissionListSchemaOut], tags=['权限'], auth=None)
@paginate
def list_permissions(request, tenant_id: str,  parent_id: str = None):
    '''
    权限列表
    '''
    permissions = Permission.valid_objects.filter(
        tenant_id=tenant_id
    )
    if parent_id:
        permissions = permissions.filter(parent_id=parent_id)
    return permissions


@api.get("/{tenant_id}/permission/{permission_id}", response=PermissionDetailSchemaOut, tags=['权限'], auth=None)
def get_permission(request, tenant_id: str, permission_id: str):
    '''
    获取权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    return permission


@api.put("/{tenant_id}/permission/{permission_id}", tags=['权限'], auth=None)
def update_permission(request, tenant_id: str, permission_id: str, data: PermissionSchemaIn):
    '''
    修改权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    permission.name = data.name
    permission.category = data.category
    if data.parent_id:
        permission.parent_id = data.parent_id
    if data.app_id:
        permission.app_id = data.app_id
    permission.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}


@api.delete("/{tenant_id}/permission/{permission_id}", tags=['权限'], auth=None)
def delete_permission(request, tenant_id: str, permission_id: str):
    '''
    删除权限
    '''
    permission = get_object_or_404(Permission, id=permission_id, is_del=False)
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    permission.delete()
    return {'error': ErrorCode.OK.value}
