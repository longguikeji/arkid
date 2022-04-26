from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/account_lifes/", tags=[_("账号生命周期")])
def get_account_life_list(request, tenant_id: str):
    """ 账号生命周期配置列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/account_lifes/{id}/", tags=[_("账号生命周期配置")])
def get_account_life(request, tenant_id: str, id: str):
    """ 获取账号生命周期配置,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/account_lifes/", tags=[_("账号生命周期配置")])
def create_account_life(request, tenant_id: str):
    """ 创建账号生命周期配置,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/account_lifes/{id}/", tags=[_("账号生命周期配置")])
def update_account_life(request, tenant_id: str, id: str):
    """ 编辑账号生命周期配置,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/account_lifes/{id}/", tags=[_("账号生命周期配置")])
def delete_account_life(request, tenant_id: str, id: str):
    """ 删除账号生命周期配置,TODO
    """
    return {}


