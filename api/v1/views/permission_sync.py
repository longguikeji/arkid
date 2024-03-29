from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN


@api.get("/tenant/{tenant_id}/permission_syncs/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_syncs(request, tenant_id: str):
    """ 权限数据同步配置列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/permission_syncs/{id}/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_sync(request, tenant_id: str, id: str):
    """ 获取权限数据同步配置,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/permission_syncs/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission_sync(request, tenant_id: str):
    """ 创建权限数据同步配置,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/permission_syncs/{id}/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permission_sync(request, tenant_id: str, id: str):
    """ 编辑权限数据同步配置,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/permission_syncs/{id}/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission_sync(request, tenant_id: str, id: str):
    """ 删除权限数据同步配置,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/permission_syncs/{id}/sync/", tags=["权限数据同步配置"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def permission_sync(request, tenant_id: str, id: str):
    """ 同步权限数据,TODO
    """
    return {}
