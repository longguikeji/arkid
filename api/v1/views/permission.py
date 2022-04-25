from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/permissions/", tags=[_("权限")])
def get_permissions(request, tenant_id: str):
    """ 权限列表,TODO
    """
    return []

@api.get(operation_id="",path="/tenant/{tenant_id}/permissions/{id}/", tags=[_("权限")])
def get_permission(request, tenant_id: str, id: str):
    """ 获取权限,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/permissions/", tags=[_("权限")])
def create_permission(request, tenant_id: str):
    """ 创建权限,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/permissions/{id}/", tags=[_("权限")])
def update_permission(request, tenant_id: str, id: str):
    """ 编辑权限,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/permissions/{id}/", tags=[_("权限")])
def delete_permission(request, tenant_id: str, id: str):
    """ 删除权限,TODO
    """
    return {}


