from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/permission_groups/", tags=[_("权限分组")])
def get_permission_groups(request, tenant_id: str):
    """ 权限分组列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/permission_groups/{id}/", tags=[_("权限分组")])
def get_permission_group(request, tenant_id: str, id: str):
    """ 获取权限分组,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/permission_groups/", tags=[_("权限分组")])
def create_permission_group(request, tenant_id: str):
    """ 创建权限分组,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/permission_groups/{id}/", tags=[_("权限分组")])
def update_permission_group(request, tenant_id: str, id: str):
    """ 编辑权限分组,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/permission_groups/{id}/", tags=[_("权限分组")])
def delete_permission_group(request, tenant_id: str, id: str):
    """ 删除权限分组,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", tags=[_("权限分组")])
def get_permissions_from_group(request, tenant_id: str, group_id: str):
    """ 获取当前分组的权限列表,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/{id}/", tags=[_("权限分组")])
def remove_permission_from_group(request, tenant_id: str, permission_group_id: str,id:str):
    """ 将权限移除出权限分组,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", tags=[_("权限分组")])
def update_permissions_from_group(request, tenant_id: str, group_id: str):
    """ 更新当前分组的权限列表,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/select_permissions/", tags=[_("权限分组")])
def get_select_permissions(request, tenant_id: str, group_id: str):
    """ 获取所有权限并附加是否在当前分组的状态,TODO
    """
    return {}


