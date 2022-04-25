from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/manager_log/", tags=[_("日志管理")])
def get_manager_logs(request, tenant_id: str):
    """ 获取租户管理员行为日志,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/user_log/", tags=[_("日志管理")])
def get_user_logs(request, tenant_id: str):
    """ 获取用户行为日志,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/log/{id}/", tags=[_("日志管理")])
def get_log(request, tenant_id: str,id:str):
    """ 获取日志详情,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/log_config/", tags=[_("日志管理")])
def get_log_config(request, tenant_id: str):
    """ 获取日志配置,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/log_config/", tags=[_("日志管理")])
def update_log_config(request, tenant_id: str):
    """ 更新日志配置,TODO
    """
    return []
