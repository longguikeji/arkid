from arkid.core.api import api
from arkid.core.translation import gettext_default as _

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/",tags=[_("用户分组")])
def get_user_group_permissions(request, tenant_id: str,user_group_id:str):
    """ 用户分组权限列表,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/",tags=[_("用户分组")])
def update_user_group_permissions(request, tenant_id: str,user_group_id:str):
    """ 更新用户分组权限列表,TODO
    """
    return []

@api.delete("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/{id}/",tags=[_("用户分组")])
def delete_user_group_permissions(request, tenant_id: str,user_group_id:str,id:str):
    """ 删除用户分组权限,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/all_permissions/",tags=[_("用户分组")])
def get_user_group_all_permissions(request, tenant_id: str,user_group_id:str):
    """ 获取所有权限并附带是否已授权给用户分组状态,TODO
    """
    return []