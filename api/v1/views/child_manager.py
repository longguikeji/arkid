from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/child_managers/", tags=["子管理员"],auth=None)
def get_child_managers(request, tenant_id: str):
    """ 子管理员列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"],auth=None)
def get_child_manager(request, tenant_id: str, id: str):
    """ 获取子管理员,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/child_managers/", tags=["子管理员"],auth=None)
def create_child_manager(request, tenant_id: str):
    """ 创建子管理员,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"],auth=None)
def update_child_manager(request, tenant_id: str, id: str):
    """ 编辑子管理员,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/child_managers/{id}/", tags=["子管理员"],auth=None)
def delete_child_manager(request, tenant_id: str, id: str):
    """ 删除子管理员,TODO
    """
    return {}


