from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/app_groups/", tags=[_("应用分组")])
def get_app_groups(request, tenant_id: str):
    """ 应用分组列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/app_groups/{id}/", tags=[_("应用分组")])
def get_app_group(request, tenant_id: str, id: str):
    """ 获取应用分组,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/app_groups/", tags=[_("应用分组")])
def create_app_group(request, tenant_id: str):
    """ 创建应用分组,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/app_groups/{id}/", tags=[_("应用分组")])
def update_app_group(request, tenant_id: str, id: str):
    """ 编辑应用分组,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/app_groups/{id}/", tags=[_("应用分组")])
def delete_app_group(request, tenant_id: str, id: str):
    """ 删除应用分组,TODO
    """
    return {}


