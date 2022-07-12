from arkid.core.models import User, SystemPermission
from ninja.pagination import paginate
from arkid.core.error import ErrorCode, ErrorDict
from typing import Union, Literal, List
from arkid.core.api import api, operation
from api.v1.schema.child_manager import *
from arkid.core.event import Event, dispatch_event
from arkid.core.pagenation import CustomPagination
from arkid.core.translation import gettext_default as _
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.event import(
    ADD_USER_MANY_PERMISSION,
)


@api.get("/tenant/{tenant_id}/child_managers/", response=List[ChildManagerListOut], tags=["子管理员"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_child_managers(request, tenant_id: str):
    """ 子管理员列表
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    users = User.valid_objects.filter(tenant=tenant)
    permissiondata = PermissionData()
    child_mans = permissiondata.get_child_mans(users, tenant)
    return child_mans

@api.get("/tenant/{tenant_id}/child_managers/{id}/", response=ChildManagerDeatilBaseOut, tags=["子管理员"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_child_manager(request, tenant_id: str, id: str):
    """ 获取子管理员
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    user = User.valid_objects.filter(tenant=tenant, id=id).first()
    # 获取子管理员的权限列表，获取子管理员的分组列表
    permissions = []
    manager_scope = []
    pd = PermissionData()
    permissions, manager_scope, self_source_ids = pd.get_child_manager_info(str(tenant.id), user)
    return {'data': {'permissions': permissions, 'manager_scope': manager_scope}}

@api.post("/tenant/{tenant_id}/child_managers/", tags=["子管理员"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_child_manager(request, tenant_id: str, data: ChildManagerCreateSchemaIn):
    """ 创建子管理员
    """
    user_ids_1 = data.users
    user_ids = []
    for user_ids_item in user_ids_1:
        user_ids.append(user_ids_item.id)
    permission_ids_1 = data.permissions
    permission_ids = []
    for permission_ids_item in permission_ids_1:
        permission_ids.append(permission_ids_item.id)
    manager_scope_ids_1 = data.manager_scope
    manager_scope_ids = []
    for manager_scope_ids_item in manager_scope_ids_1:
        manager_scope_ids.append(manager_scope_ids_item.id)
    if user_ids and permission_ids and manager_scope_ids:
        dispatch_event(Event(tag=ADD_USER_MANY_PERMISSION, tenant=request.tenant, request=request, data={
            'user_ids': user_ids,
            'tenant_id': tenant_id,
            'data_arr': permission_ids+manager_scope_ids
        }))
    return ErrorDict(ErrorCode.OK)

@api.post("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_child_manager(request, tenant_id: str, id: str, data: ChildManagerEditSchemaIn):
    """ 编辑子管理员
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    permission_ids_1 = data.permissions
    permission_ids = []
    for permission_ids_item in permission_ids_1:
        permission_ids.append(str(permission_ids_item.id))
    manager_scope_ids_1 = data.manager_scope
    manager_scope_ids = []
    for manager_scope_ids_item in manager_scope_ids_1:
        manager_scope_ids.append(str(manager_scope_ids_item.id))
    user = User.valid_objects.filter(tenant=tenant, id=id).first()
    permissiondata = PermissionData()
    # 重新查一次
    permissions_1, manager_scope_1, self_source_ids = permissiondata.get_child_manager_info(str(tenant.id), user)
    for self_source_id in self_source_ids:
        if self_source_id in permission_ids:
            # 去掉分组权限
            permission_ids.remove(self_source_id)
        elif self_source_id in manager_scope_ids:
            manager_scope_ids.remove(self_source_id)
        else:
            # 直接提示移除了分组权限
            return ErrorDict(ErrorCode.BAN_REMOVE_GROUP_PERMISSION)
        # if self_source_id in manager_scope_ids:
        #     # 去掉分组权限
        #     manager_scope_ids.remove(self_source_id)
        # else:
        #     # 直接提示移除了分组范围
        #     return ErrorDict(ErrorCode.BAN_REMOVE_GROUP_SCOPE)
    # 先删除管理员在重新加权限
    permissiondata.delete_child_man(user, tenant)
    # 重新加权限
    if permission_ids and manager_scope_ids:
        # permissiondata.add_user_many_permission({
        #     'user_ids': [str(user.id)],
        #     'tenant_id': tenant_id,
        #     'data_arr': permission_ids+manager_scope_ids
        # })
        dispatch_event(Event(tag=ADD_USER_MANY_PERMISSION, tenant=tenant, request=request, data={
            'user_ids': [str(user.id)],
            'tenant_id': tenant_id,
            'data_arr': permission_ids+manager_scope_ids
        }))
    return ErrorDict(ErrorCode.OK)

@api.delete("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_child_manager(request, tenant_id: str, id: str):
    """ 删除子管理员
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    user = User.valid_objects.filter(tenant=tenant, id=id).first()
    permissiondata = PermissionData()
    permissiondata.delete_child_man(user, tenant)
    return ErrorDict(ErrorCode.OK)


