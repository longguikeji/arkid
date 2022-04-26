from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenants/", tags=[_("租户管理")])
def get_tenant_list(request):
    """ 获取租户管理员行为日志,TODO
    """
    return []

@api.get("/tenants/{id}/", tags=[_("租户管理")])
def get_tenant(request, id: str):
    """ 获取租户,TODO
    """
    return {}

@api.post("/tenants/", tags=[_("租户管理")])
def create_tenant(request, tenant_id: str):
    """ 创建租户,TODO
    """
    return {}

@api.put("/tenants/{id}/", tags=[_("租户管理")])
def update_tenant(request, id: str):
    """ 编辑租户,TODO
    """
    return {}

@api.delete("/tenants/{id}/", tags=[_("租户管理")])
def delete_tenant(request, id: str):
    """ 删除租户,TODO
    """
    return {}

@api.get("/tenants/{id}/config/", tags=[_("租户管理")])
def get_tenant_config(request, id: str):
    """ 获取租户配置,TODO
    """
    return {}

@api.post("/tenants/{id}/config/", tags=[_("租户管理")])
def update_tenant_config(request, id: str):
    """ 编辑租户配置,TODO
    """
    return {}