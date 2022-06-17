
from arkid.core.api import api, operation
from typing import List, Optional
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Permission, SystemPermission
from django.shortcuts import get_object_or_404
from arkid.core.event import Event, dispatch_event
from arkid.core.event import(
    CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION,
    ADD_USER_SYSTEM_PERMISSION, ADD_USER_APP_PERMISSION,
    REMOVE_USER_SYSTEM_PERMISSION, REMOVE_USER_APP_PERMISSION, OPEN_APP_PERMISSION,
    OPEN_SYSTEM_PERMISSION, CLOSE_SYSTEM_PERMISSION, CLOSE_APP_PERMISSION,
)
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from api.v1.schema.permission import *

import uuid


@transaction.atomic
@api.post("/tenant/{tenant_id}/permissions", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission(request, tenant_id: str, data: PermissionCreateSchemaIn):
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
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/permissions", response=List[PermissionListSchemaOut], tags=['权限'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_permissions(request, tenant_id: str,  app_id: str = None, select_user_id: str = None, group_id: str = None):
    '''
    权限列表
    '''
    login_user = request.user
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_permissions_by_search(tenant_id, app_id, select_user_id, group_id, login_user)

@api.get("/tenant/{tenant_id}/permission/{permission_id}", response=PermissionDetailOut, tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission(request, tenant_id: str, permission_id: str):
    '''
    获取权限
    '''
    permission = Permission.valid_objects.filter(id=permission_id).first()
    if permission is None:
        return ErrorDict(ErrorCode.PERMISSION_NOT_EDIT)
    return {'data': permission}


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
    return ErrorDict(ErrorCode.OK)


@api.delete("/tenant/{tenant_id}/permission/{permission_id}", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission(request, tenant_id: str, permission_id: str):
    '''
    删除权限
    '''
    permission = Permission.valid_objects.filter(id=permission_id).first()
    if permission is None:
        return ErrorDict(ErrorCode.PERMISSION_NOT_EDIT)
    permission.delete()
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/permissionstr", tags=['权限'], response=PermissionStrSchemaOut)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
def get_permission_str(request, tenant_id: str,  app_id: str = None):
    '''
    权限结果字符串
    '''
    from arkid.core.models import User
    user = request.user
    # user, _ = User.objects.get_or_create(
    #     username="hanbin",
    # )
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_permission_str(user, tenant_id, app_id)


@api.get("/app/permission_result", tags=['权限'], response=PermissionStrSchemaOut, auth=None)
def get_arkstore_permission_str(request):
    '''
    获取应用权限字符串(二进制)
    '''
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.id_token_to_permission_str(request)


@api.get("/app/permission_result/bin", tags=['权限'], response=PermissionStrSchemaOut, auth=None)
def get_arkstore_permission_str(request):
    '''
    获取应用权限字符串(base64结果中的0b1不做计算)
    '''
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.id_token_to_permission_str(request, True)


@api.post("/tenant/{tenant_id}/permission/user/{select_user_id}/add_permission", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def user_add_permission(request, tenant_id: str, select_user_id: str, data: PermissionBatchSchemaIn):
    '''
    添加用户权限
    '''
    data_arr = data.data
    for permission_id in data_arr:
        permission = SystemPermission.valid_objects.filter(id=permission_id).first()
        if permission is None:
            permission = Permission.valid_objects.filter(id=permission_id).first()
        permission.user_id = select_user_id
        if isinstance(permission, SystemPermission):
            # 添加系统权限
            dispatch_event(Event(tag=ADD_USER_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=permission))
        else:
            # 添加应用权限
            dispatch_event(Event(tag=ADD_USER_APP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/permission/user/{select_user_id}/{permission_id}/remove_permission", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def user_remove_permission(request, tenant_id: str, select_user_id: str, permission_id: str):
    '''
    移除用户权限
    '''
    permission = SystemPermission.valid_objects.filter(id=permission_id).first()
    if permission is None:
        permission = Permission.valid_objects.filter(id=permission_id).first()
    permission.user_id = select_user_id
    if isinstance(permission, SystemPermission):
        dispatch_event(Event(tag=REMOVE_USER_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=permission))
    else:
        dispatch_event(Event(tag=REMOVE_USER_APP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/permission/{permission_id}/set_open", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_set_open(request, tenant_id: str, permission_id: str):
    '''
    权限外部访问打开
    '''
    permission = SystemPermission.valid_objects.filter(
        tenant_id=tenant_id,
        id=permission_id
    ).first()
    if permission is None:
        permission = Permission.valid_objects.filter(tenant_id=tenant_id, id=permission_id).first()
    if permission:
        permission.is_open = True
        permission.save()
        if isinstance(permission, SystemPermission):
            dispatch_event(Event(tag=OPEN_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=permission))
        else:
            dispatch_event(Event(tag=OPEN_APP_PERMISSION, tenant=request.tenant, request=request, data=permission))
        return ErrorDict(ErrorCode.OK)
    else:
        return ErrorDict(ErrorCode.PERMISSION_EXISTS_ERROR)


@api.post("/tenant/{tenant_id}/permissions/batch_open", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_batch_open(request, tenant_id: str, data: PermissionBatchSchemaIn):
    '''
    权限外部访问批量打开
    '''
    data_arr = data.data
    system_permissions = SystemPermission.valid_objects.filter(
        tenant_id=tenant_id,
        id__in=data_arr
    )
    permissions = Permission.valid_objects.filter(
        tenant_id=tenant_id,
        id__in=data_arr
    )
    if system_permissions:
        system_permissions.update(is_open=True)
        dispatch_event(Event(tag=OPEN_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=None))
    if permissions:
        permissions.update(is_open=True)
        dispatch_event(Event(tag=OPEN_APP_PERMISSION, tenant=request.tenant, request=request, data=None))
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/permissions/batch_close", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_batch_close(request, tenant_id: str, data: PermissionBatchSchemaIn):
    '''
    权限外部访问批量关闭
    '''
    from arkid.core.perm.permission_data import PermissionData
    permission_data = PermissionData()
    data_arr = data.data
    system_permissions = SystemPermission.valid_objects.filter(
        tenant_id=tenant_id,
        id__in=data_arr
    )
    permissions = Permission.valid_objects.filter(
        tenant_id=tenant_id,
        id__in=data_arr
    )
    if system_permissions:
        system_permissions.update(is_open=False)
        system_permissions_info = []
        for system_permission in system_permissions:
            system_permissions_info.append({
                'sort_id': system_permission.sort_id,
                'tenant_id': system_permission.tenant_id,
            })
        dispatch_event(Event(tag=CLOSE_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=system_permissions_info))
    if permissions:
        permissions.update(is_open=False)
        app_permissions_info = []
        for permission in permissions:
            app_permissions_info.append({
                'app_id': permission.app_id,
                'sort_id': permission.sort_id,
                'tenant_id': permission.tenant_id,
            })
        dispatch_event(Event(tag=CLOSE_APP_PERMISSION, tenant=request.tenant, request=request, data=app_permissions_info))
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/permission/{permission_id}/set_close", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_set_close(request, tenant_id: str, permission_id: str):
    '''
    权限外部访问关闭
    '''
    permission = SystemPermission.valid_objects.filter(
        tenant_id=tenant_id,
        id=permission_id
    ).first()
    if permission is None:
        permission = Permission.valid_objects.filter(tenant_id=tenant_id, id=permission_id).first()
    if permission:
        permission.is_open = False
        permission.save()
        if isinstance(permission, SystemPermission):
            system_permissions_info = []
            system_permissions_info.append({
                'sort_id': permission.sort_id,
                'tenant_id': permission.tenant_id,
            })
            dispatch_event(Event(tag=CLOSE_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=system_permissions_info))
        else:
            app_permissions_info = []
            app_permissions_info.append({
                'app_id': permission.app_id,
                'sort_id': permission.sort_id,
                'tenant_id': permission.tenant_id,
            })
            dispatch_event(Event(tag=CLOSE_APP_PERMISSION, tenant=request.tenant, request=request, data=app_permissions_info))
        return ErrorDict(ErrorCode.OK)
    else:
        return ErrorDict(ErrorCode.PERMISSION_EXISTS_ERROR)


@api.post("/tenant/{tenant_id}/permission/{permission_id}/toggle_open", tags=['权限'], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_toggle_open(request, tenant_id: str, permission_id: str):
    '''
    切换权限是否打开的状态
    '''
    permission = SystemPermission.valid_objects.filter(
        tenant_id=tenant_id,
        id=permission_id
    ).first()
    if permission is None:
        permission = Permission.valid_objects.filter(tenant_id=tenant_id, id=permission_id).first()
    if permission:
        is_open = permission.is_open
        if is_open:
            # 原来是打开，现在是关闭
            permission.is_open = False
            permission.save()
            if isinstance(permission, SystemPermission):
                system_permissions_info = []
                system_permissions_info.append({
                    'sort_id': permission.sort_id,
                    'tenant_id': permission.tenant_id,
                })
                dispatch_event(Event(tag=CLOSE_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=system_permissions_info))
            else:
                app_permissions_info = []
                app_permissions_info.append({
                    'app_id': permission.app_id,
                    'sort_id': permission.sort_id,
                    'tenant_id': permission.tenant_id,
                })
                dispatch_event(Event(tag=CLOSE_APP_PERMISSION, tenant=request.tenant, request=request, data=app_permissions_info))
        else:
            # 原来是关闭，现在是打开
            permission.is_open = True
            permission.save()
            if isinstance(permission, SystemPermission):
                dispatch_event(Event(tag=OPEN_SYSTEM_PERMISSION, tenant=request.tenant, request=request, data=permission))
            else:
                dispatch_event(Event(tag=OPEN_APP_PERMISSION, tenant=request.tenant, request=request, data=permission))
        return {'error': ErrorCode.OK.value}
    else:
        return ErrorDict(ErrorCode.PERMISSION_EXISTS_ERROR)