from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/auth_rules/", tags=["认证规则"],auth=None)
def get_auth_rules(request, tenant_id: str):
    """ 认证规则列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/auth_rules/{id}/", tags=["认证规则"],auth=None)
def get_auth_rule(request, tenant_id: str, id: str):
    """ 获取认证规则,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/auth_rules/", tags=["认证规则"],auth=None)
def create_auth_rule(request, tenant_id: str):
    """ 创建认证规则,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/auth_rules/{id}/", tags=["认证规则"],auth=None)
def update_auth_rule(request, tenant_id: str, id: str):
    """ 编辑认证规则,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/auth_rules/{id}/", tags=["认证规则"],auth=None)
def delete_auth_rule(request, tenant_id: str, id: str):
    """ 删除认证规则,TODO
    """
    return {}


