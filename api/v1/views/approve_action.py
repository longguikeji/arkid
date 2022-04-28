from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/approve_actions/", tags=["审批动作"],auth=None)
def get_approve_actions(request, tenant_id: str):
    """ 审批动作列表,TODO
    """
    return []

@api.get(operation_id="",path="/tenant/{tenant_id}/approve_actions/{id}/", tags=["审批动作"],auth=None)
def get_approve_action(request, tenant_id: str, id: str):
    """ 获取审批动作,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/approve_actions/", tags=["审批动作"],auth=None)
def create_approve_action(request, tenant_id: str):
    """ 创建审批动作,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/approve_actions/{id}/", tags=["审批动作"],auth=None)
def update_approve_action(request, tenant_id: str, id: str):
    """ 编辑审批动作,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/approve_actions/{id}/", tags=["审批动作"],auth=None)
def delete_approve_action(request, tenant_id: str, id: str):
    """ 删除审批动作,TODO
    """
    return {}


