from arkid.core.api import api
from arkid.core.translation import gettext_default as _

@api.get("/tenant/{tenant_id}/user_groups/", tags=["用户分组"],auth=None)
def get_user_groups(request, tenant_id: str):
    """ 用户分组列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/user_groups/{id}/", tags=["用户分组"],auth=None)
def get_user_group(request, tenant_id: str, id: str):
    """ 获取用户分组,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/user_groups/", tags=["用户分组"],auth=None)
def create_user_group(request, tenant_id: str):
    """ 创建用户分组,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/user_groups/{id}/", tags=["用户分组"],auth=None)
def update_user_group(request, tenant_id: str, id: str):
    """ 编辑用户分组,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/user_groups/{id}/", tags=["用户分组"],auth=None)
def delete_user_group(request, tenant_id: str, id: str):
    """ 删除用户分组,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/users/", tags=["用户分组"],auth=None)
def get_users_from_group(request, tenant_id: str, user_group_id: str):
    """ 获取当前分组的用户列表,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/user_groups/{user_group_id}/users/{id}/", tags=["用户分组"],auth=None)
def remove_user_from_group(request, tenant_id: str, user_group_id: str,id:str):
    """ 将用户移除出用户分组,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/user_groups/{user_group_id}/users/", tags=["用户分组"],auth=None)
def update_users_from_group(request, tenant_id: str, user_group_id: str):
    """ 更新当前分组的用户列表,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/select_users/", tags=["用户分组"],auth=None)
def get_select_users(request, tenant_id: str, user_group_id: str):
    """ 获取所有用户并附加是否在当前分组的状态,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/",tags=["用户分组"],auth=None)
def get_user_group_permissions(request, tenant_id: str,user_group_id:str):
    """ 用户分组权限列表,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/",tags=["用户分组"],auth=None)
def update_user_group_permissions(request, tenant_id: str,user_group_id:str):
    """ 更新用户分组权限列表,TODO
    """
    return []

@api.delete("/tenant/{tenant_id}/user_groups/{user_group_id}/permissions/{id}/",tags=["用户分组"],auth=None)
def delete_user_group_permissions(request, tenant_id: str,user_group_id:str,id:str):
    """ 删除用户分组权限,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/user_groups/{user_group_id}/all_permissions/",tags=["用户分组"],auth=None)
def get_user_group_all_permissions(request, tenant_id: str,user_group_id:str):
    """ 获取所有权限并附带是否已授权给用户分组状态,TODO
    """
    return []