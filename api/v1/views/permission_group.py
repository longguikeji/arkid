from uuid import UUID
from ninja import Query
from typing import List
from ninja import Field
from ninja import Schema
from ninja import ModelSchema
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.api import api, operation
from django.shortcuts import get_object_or_404
from arkid.core.models import Permission, SystemPermission, App, Tenant
from arkid.core.event import Event, dispatch_event
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.event import (
    CREATE_GROUP_PERMISSION, UPDATE_GROUP_PERMISSION, DELETE_GROUP_PERMISSION,
    REMOVE_GROUP_PERMISSION_PERMISSION, UPDATE_GROUP_PERMISSION_PERMISSION,
)
from arkid.core.translation import gettext_default as _
from api.v1.schema.permission_group import *

import uuid


@api.get("/tenant/{tenant_id}/permission_groups/", tags=["权限分组"], response=List[PermissionGroupListSchemaOut])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_permission_groups(request, tenant_id: str,  parent_id: str = None,  app_id: str = None):
    """ 权限分组列表
    """
    # 只允许非系统并且有应用的分组编辑
    if parent_id == 'arkid':
        app_id = parent_id
        parent_id = None
    if parent_id:
        app = App.valid_objects.filter(
            id=parent_id
        ).first()
        if app:
            parent_id = None
            app_id = str(app.id)
    login_user = request.user
    from arkid.core.perm.permission_data import PermissionData
    permissiondata = PermissionData()
    return permissiondata.get_permissions_by_search(tenant_id, app_id, None, None, login_user, parent_id, True)


@api.get("/tenant/{tenant_id}/permission_groups/{id}/", response=PermissionGroupDetailSchemaOut, tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_group(request, tenant_id: str, id: str):
    """ 获取权限分组
    """
    permission = Permission.valid_objects.filter(category='group', id=id).first()
    if permission is None:
        permission = SystemPermission.valid_objects.filter(category='group', id=id).first()
    if permission:
        return {'data': permission}
    else:
        return ErrorDict(ErrorCode.PERMISSION_EXISTS_ERROR)

@transaction.atomic
@api.post("/tenant/{tenant_id}/permission_groups/", tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission_group(request, tenant_id: str, data: PermissionGroupSchemaIn):
    """ 创建权限分组
    """
    if data.app.id != 'arkid':
        permission = Permission()
    else:
        permission = SystemPermission()
    permission.tenant = Tenant.valid_objects.filter(id=tenant_id).first()
    permission.name = data.name
    permission.category = 'group'
    permission.code = 'other_{}'.format(uuid.uuid4())
    if data.parent:
        permission.parent = Permission.valid_objects.filter(id=data.parent.id).first()
    if data.app.id != 'arkid':
        permission.app = App.valid_objects.filter(id=data.app.id).first()
    permission.is_system = False
    permission.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=CREATE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}

@api.put("/tenant/{tenant_id}/permission_groups/{id}/", tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permission_group(request, tenant_id: str, id: str, data: PermissionGroupEditSchemaIn):
    """ 编辑权限分组
    """
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False, category='group')
    # else:
    #     permission = get_object_or_404(Permission, id=id, is_del=False, category='group')
    # permission = SystemPermission.valid_objects.filter(id=id, category='group').first()
    # if permission is None:
    permission = Permission.valid_objects.filter(id=id, category='group').first()
    if permission is None:
        permission = SystemPermission.valid_objects.filter(category='group', id=id).first()
    permission.name = data.name
    if data.parent:
        permission.parent = Permission.valid_objects.filter(id=data.parent.id).first()
    # if data.app_id:
    #     permission.app_id = data.app_id
    permission.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)

@api.delete("/tenant/{tenant_id}/permission_groups/{id}/", tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission_group(request, tenant_id: str, id: str):
    """ 删除权限分组
    """
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False, category='group')
    # else:
    #     permission = get_object_or_404(Permission, id=id, is_del=False, category='group')
    permission = SystemPermission.valid_objects.filter(id=id, category='group').first()
    if permission is None:
        permission = Permission.valid_objects.filter(id=id, category='group').first()
    permission.delete()
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return ErrorDict(ErrorCode.OK)

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", response=List[PermissionListSchemaOut], tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_permissions_from_group(request, tenant_id: str, permission_group_id: str, query_data:PermissionGroupListQueryIn=Query(...)):
    """ 获取当前分组的权限列表
    """
    category = query_data.category
    operation_id = query_data.operation_id
    name = query_data.name
    app_name = query_data.app_name
    from arkid.core.perm.permission_data import PermissionData
    if permission_group_id != 'arkid':
        permission = SystemPermission.valid_objects.filter(id=permission_group_id).first()
        if permission is None:
            permission = Permission.valid_objects.filter(id=permission_group_id).first()
        if permission:
            result_items = permission.container.all()
            if category:
                category = category.strip()
                result_items = result_items.filter(category__icontains=category)
            if operation_id:
                operation_id = operation_id.strip()
                result_items = result_items.filter(operation_id__icontains=operation_id)
            if name:
                name = name.strip()
                result_items = result_items.filter(name__icontains=name)
            if app_name:
                app_name = app_name.strip()
                if isinstance(permission, SystemPermission):
                    permissions = permissions.filter(app__name__icontains=app_name)
                else:
                    filter_apps = App.valid_objects.filter(
                        name__icontains=app_name
                    )
                    filter_ids = []
                    for filter_app in filter_apps:
                        filter_ids.append(filter_app.entry_permission.id)
                    if filter_ids:
                        result_items = result_items.filter(id__in=filter_ids)
                    else:
                        result_items = result_items.filter(id__isnull=True)
            return result_items
        else:
            app = App.valid_objects.filter(id=permission_group_id).first()
            items = []
            if app:
                app_permission_ids = []
                base_permissions = Permission.valid_objects.filter(
                    app_id=app.id,
                )
                group_permissions = base_permissions.filter(
                    category='group',
                    # 权限分组需要放出其它权限
                    #code__startswith='group_role'
                )
                if group_permissions:
                    if category:
                        category = category.strip()
                        group_permissions = group_permissions.filter(category__icontains=category)
                    if operation_id:
                        operation_id = operation_id.strip()
                        group_permissions = group_permissions.filter(operation_id__icontains=operation_id)
                    if name:
                        name = name.strip()
                        group_permissions = group_permissions.filter(name__icontains=name)
                    if app_name:
                        app_name = app_name.strip()
                        group_permissions = group_permissions.filter(app__name__icontains=app_name)
                    items.extend(group_permissions)
                for group_permission in group_permissions:
                    for item in group_permission.container.all():
                        if item.id not in app_permission_ids:
                            app_permission_ids.append(item.id)
                if app_permission_ids:
                    group_permission_details = base_permissions.filter(
                        category='api',
                    ).exclude(id__in=app_permission_ids)
                    if group_permission_details:
                        if category:
                            category = category.strip()
                            group_permission_details = group_permission_details.filter(category__icontains=category)
                        if operation_id:
                            operation_id = operation_id.strip()
                            group_permission_details = group_permission_details.filter(operation_id__icontains=operation_id)
                        if name:
                            name = name.strip()
                            group_permission_details = group_permission_details.filter(name__icontains=name)
                        if app_name:
                            app_name = app_name.strip()
                            group_permissions = group_permissions.filter(app__name__icontains=app_name)
                        items.extend(group_permission_details)
                entry_permission = None
                if app.entry_permission:
                    if category and operation_id and name and category in app.entry_permission.category and operation_id in app.entry_permission.operation_id and name in app.entry_permission.name:
                        entry_permission = app.entry_permission
                    elif category and operation_id and category in app.entry_permission.category and operation_id in app.entry_permission.operation_id:
                        entry_permission = app.entry_permission
                    elif category and name and category in app.entry_permission.category and name in app.entry_permission.name:
                        entry_permission = app.entry_permission
                    elif operation_id and name and operation_id in app.entry_permission.operation_id and name in app.entry_permission.name:
                        entry_permission = app.entry_permission
                    elif category and category in app.entry_permission.category:
                        entry_permission = app.entry_permission
                    elif operation_id and operation_id in app.entry_permission.operation_id:
                        entry_permission = app.entry_permission
                    elif name and name in app.entry_permission.name:
                        entry_permission = app.entry_permission
                    if category is None and operation_id is None and name is None and app.entry_permission:
                        entry_permission = app.entry_permission
                    if app_name and app_name not in app.name:
                        entry_permission = None
                # 需要过滤展示
                permissiondata = PermissionData()
                items = permissiondata.get_permissions_by_app_filter(tenant_id, app.id, items, entry_permission, request.user)
            return items
    else:
        permissions = SystemPermission.valid_objects.filter(category='group', is_system=True)
        if category:
            category = category.strip()
            permissions = permissions.filter(category__icontains=category)
        if operation_id:
            operation_id = operation_id.strip()
            permissions = permissions.filter(operation_id__icontains=operation_id)
        if name:
            name = name.strip()
            permissions = permissions.filter(name__icontains=name)
        if app_name:
            app_name = app_name.strip()
            filter_apps = App.valid_objects.filter(
                name__icontains=app_name
            )
            filter_ids = []
            for filter_app in filter_apps:
                filter_ids.append(filter_app.entry_permission.id)
            if filter_ids:
                permissions = permissions.filter(id__in=filter_ids)
            else:
                permissions = permissions.filter(id__isnull=True)
        # 只能看到自己拥有的权限
        permissiondata = PermissionData()
        return permissiondata.get_system_permission_by_filter(tenant_id, permissions, request.user)
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False)
    # else:
    #     permission = get_object_or_404(Permission, id=permission_group_id, is_del=False)
    

@api.delete("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/{id}/", tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def remove_permission_from_group(request, tenant_id: str, permission_group_id: str, id:str):
    """ 将权限移除出权限分组
    """
    # 只允许非arkid的操作
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission_group = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False, category='group')
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False)
    # else:
    permission_group = SystemPermission.valid_objects.filter(id=permission_group_id, category='group', is_system=False).first()
    if permission_group is None:
        permission_group = Permission.valid_objects.filter(id=permission_group_id, category='group', is_system=False).first()
        permission = Permission.valid_objects.filter(id=id).first()
    else:
        permission = SystemPermission.valid_objects.filter(id=id).first()

    if permission_group and permission:
        permission_group.container.remove(permission)
        describe = permission_group.describe
        sort_ids = describe.get('sort_ids', [])
        sort_ids.append(permission.sort_id)
        permission_group.describe = describe
        permission_group.save()
        # 分发事件开始
        # dispatch_event(Event(tag=REMOVE_GROUP_PERMISSION_PERMISSION, tenant=request.tenant, request=request, data=permission_group))
        # 分发事件结束
        return {'error': ErrorCode.OK.value}
    else:
        return ErrorDict(ErrorCode.PERMISSION_GROUP_NOT_DELETE)

@api.post("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", tags=["权限分组"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permissions_from_group(request, tenant_id: str, permission_group_id: str, data: PermissionGroupPermissionSchemaIn):
    """ 更新当前分组的权限列表
    """
    # 只允许非arkid的操作
    tenant = request.tenant
    permission_group = SystemPermission.valid_objects.filter(id=permission_group_id, category='group', is_system=False).first()
    if permission_group is None:
        permission_group = Permission.valid_objects.filter(id=permission_group_id, category='group', is_system=False).first()
        permissions = Permission.valid_objects.filter(id__in=data.data)
    else:
        permissions = SystemPermission.valid_objects.filter(id__in=data.data)

    if permission_group and permissions:
        describe = permission_group.describe
        sort_ids = describe.get('sort_ids', [])
        for permission in permissions:
            sort_id = permission.sort_id
            permission_group.container.add(permission)
            sort_ids.append(sort_id)
        permission_group.describe = describe
        permission_group.save()
        # 分发事件开始
        dispatch_event(Event(tag=UPDATE_GROUP_PERMISSION_PERMISSION, tenant=tenant, request=request, data=permission_group))
        # 分发事件结束
        return ErrorDict(ErrorCode.OK)
    else:
        return ErrorDict(ErrorCode.PERMISSION_GROUP_NOT_EDIT)

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/select_permissions/", response=List[PermissionListSelectSchemaOut], tags=["权限分组"])
@operation(PermissionListDataSelectSchemaOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_select_permissions(request, tenant_id: str, permission_group_id: str, query_data:PermissionGroupListQueryIn=Query(...)):
    """ 获取所有权限并附加是否在当前分组的状态
    """
    category = query_data.category
    operation_id = query_data.operation_id
    name = query_data.name
    # 只允许非arkid的分组操作(如果用户直接在系统分组里加权限会有问题)
    if permission_group_id == 'arkid':
        return []
    permission_group = SystemPermission.valid_objects.filter(id=permission_group_id, category='group', is_system=False).first()
    if permission_group is None:
        permission_group = Permission.valid_objects.filter(id=permission_group_id, category='group').first()
    if isinstance(permission_group, SystemPermission):
        # permission_group = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False, category='group')
        containers = permission_group.container.all()
        ids = []
        for container in containers:
            ids.append(container.id.hex)

        permissions = SystemPermission.valid_objects.exclude(category='group')
        if category:
            category = category.strip()
            permissions = permissions.filter(category__icontains=category)
        if operation_id:
            operation_id = operation_id.strip()
            permissions = permissions.filter(operation_id__icontains=operation_id)
        if name:
            name = name.strip()
            permissions = permissions.filter(name__icontains=name)
        for permission in permissions:
            id_hex = permission.id.hex
            if id_hex in ids:
                permission.in_current = True
            else:
                permission.in_current = False
    elif isinstance(permission_group, Permission):
        containers = permission_group.container.all()
        ids = []
        for container in containers:
            ids.append(container.id.hex)

        permissions = Permission.valid_objects.filter(tenant=permission_group.tenant, app=permission_group.app).exclude(category='group')
        if category:
            category = category.strip()
            permissions = permissions.filter(category__icontains=category)
        if operation_id:
            operation_id = operation_id.strip()
            permissions = permissions.filter(operation_id__icontains=operation_id)
        if name:
            name = name.strip()
            permissions = permissions.filter(name__icontains=name)
        for permission in permissions:
            id_hex = permission.id.hex
            if id_hex in ids:
                permission.in_current = True
            else:
                permission.in_current = False
    else:
        permissions = []
    return list(permissions)


