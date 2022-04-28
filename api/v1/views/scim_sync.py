from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/scim_syncs/", tags=["用户数据同步配置"],auth=None)
def get_scim_syncs(request, tenant_id: str):
    """ 用户数据同步配置列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/scim_syncs/{id}/", tags=["用户数据同步配置"],auth=None)
def get_scim_sync(request, tenant_id: str, id: str):
    """ 获取用户数据同步配置,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/scim_syncs/", tags=["用户数据同步配置"],auth=None)
def create_scim_sync(request, tenant_id: str):
    """ 创建用户数据同步配置,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/scim_syncs/{id}/", tags=["用户数据同步配置"],auth=None)
def update_scim_sync(request, tenant_id: str, id: str):
    """ 编辑用户数据同步配置,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/scim_syncs/{id}/", tags=["用户数据同步配置"],auth=None)
def delete_scim_sync(request, tenant_id: str, id: str):
    """ 删除用户数据同步配置,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/scim_syncs/{id}/sync/", tags=["用户数据同步配置"],auth=None)
def scim_sync(request, tenant_id: str, id: str):
    """ 同步权限数据,TODO
    """
    return {}
