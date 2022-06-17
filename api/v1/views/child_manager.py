

from arkid.core.models import User
from ninja.pagination import paginate
from arkid.core.error import ErrorCode, ErrorDict
from typing import Union, Literal, List
from arkid.core.api import api, operation
from api.v1.schema.child_manager import *
from arkid.core.pagenation import CustomPagination
from arkid.core.translation import gettext_default as _
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN


@api.get("/tenant/{tenant_id}/child_managers/", response=List[ChildManagerListOut], tags=["子管理员"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_child_managers(request, tenant_id: str):
    """ 子管理员列表,TODO
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    users = User.valid_objects.filter(tenant=tenant)
    permissiondata = PermissionData()
    child_mans = permissiondata.get_child_mans(users, tenant)
    return child_mans

@api.get("/tenant/{tenant_id}/child_managers/{id}/", response=ChildManagerListOut, tags=["子管理员"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
def get_child_manager(request, tenant_id: str, id: str):
    """ 获取子管理员,TODO
    """
    tenant = request.tenant
    user = User.valid_objects.filter(tenant=tenant, id=id).first()
    return user

# @api.post("/tenant/{tenant_id}/child_managers/", tags=["子管理员"],auth=None)
# def create_child_manager(request, tenant_id: str):
#     """ 创建子管理员,TODO
#     """
#     return {}

# @api.put("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"],auth=None)
# def update_child_manager(request, tenant_id: str, id: str):
#     """ 编辑子管理员,TODO
#     """
#     return {}

@api.delete("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"],auth=None)
def delete_child_manager(request, tenant_id: str, id: str):
    """ 删除子管理员,TODO
    """
    from arkid.core.perm.permission_data import PermissionData
    tenant = request.tenant
    user = User.valid_objects.filter(tenant=tenant, id=id).first()
    permissiondata = PermissionData()
    permissiondata.delete_child_man(user, tenant)
    return ErrorDict(ErrorCode.OK)


