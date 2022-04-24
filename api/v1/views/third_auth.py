from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/third_auths/", tags=[_("第三方认证")])
def get_third_auths(request, tenant_id: str):
    """ 第三方认证列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/third_auths/{id}/", tags=[_("第三方认证")])
def get_third_auth(request, tenant_id: str, id: str):
    """ 获取第三方认证,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/third_auths/", tags=[_("第三方认证")])
def create_third_auth(request, tenant_id: str):
    """ 创建第三方认证,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/third_auths/{id}/", tags=[_("第三方认证")])
def update_third_auth(request, tenant_id: str, id: str):
    """ 编辑第三方认证,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/third_auths/{id}/", tags=[_("第三方认证")])
def delete_third_auth(request, tenant_id: str, id: str):
    """ 删除第三方认证,TODO
    """
    return {}


