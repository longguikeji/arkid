from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/auto_auths/", tags=[_("自动认证")])
def get_auto_auths(request, tenant_id: str):
    """ 自动认证列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/auto_auths/{id}/", tags=[_("自动认证")])
def get_auto_auth(request, tenant_id: str, id: str):
    """ 获取自动认证,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/auto_auths/", tags=[_("自动认证")])
def create_auto_auth(request, tenant_id: str):
    """ 创建自动认证,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/auto_auths/{id}/", tags=[_("自动认证")])
def update_auto_auth(request, tenant_id: str, id: str):
    """ 编辑自动认证,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/auto_auths/{id}/", tags=[_("自动认证")])
def delete_auto_auth(request, tenant_id: str, id: str):
    """ 删除自动认证,TODO
    """
    return {}


