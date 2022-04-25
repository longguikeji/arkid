from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/permission_rules/", tags=[_("授权规则")])
def get_permission_rules(request, tenant_id: str):
    """ 授权规则列表,TODO
    """
    return []

@api.get(operation_id="",path="/tenant/{tenant_id}/permission_rules/{id}/", tags=[_("授权规则")])
def get_permission_rule(request, tenant_id: str, id: str):
    """ 获取授权规则,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/permission_rules/", tags=[_("授权规则")])
def create_permission_rule(request, tenant_id: str):
    """ 创建授权规则,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/permission_rules/{id}/", tags=[_("授权规则")])
def update_permission_rule(request, tenant_id: str, id: str):
    """ 编辑授权规则,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/permission_rules/{id}/", tags=[_("授权规则")])
def delete_permission_rule(request, tenant_id: str, id: str):
    """ 删除授权规则,TODO
    """
    return {}


