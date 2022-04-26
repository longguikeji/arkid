from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenants/", tags=[_("租户管理")])
def get_tenant_list(request):
    """ 获取租户管理员行为日志,TODO
    """
    return []

@api.get("/tenants/{id}/", tags=[_("租户管理")])
def get_auth_rule(request, id: str):
    """ 获取租户,TODO
    """
    return {}

@api.post("/tenants/", tags=[_("租户管理")])
def create_auth_rule(request, tenant_id: str):
    """ 创建租户,TODO
    """
    return {}

@api.put("/tenants/{id}/", tags=[_("租户管理")])
def update_auth_rule(request, id: str):
    """ 编辑租户,TODO
    """
    return {}

@api.delete("/tenants/{id}/", tags=[_("租户管理")])
def delete_auth_rule(request, id: str):
    """ 删除租户,TODO
    """
    return {}
