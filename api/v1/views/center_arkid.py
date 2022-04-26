from arkid.core.api import api
from arkid.core.translation import gettext_default as _

@api.get("/tenant/{tenant_id}/center_arkid/", tags=[_("中心平台")])
def get_center_arkid(request, tenant_id: str):
    """ 获取中心平台配置,TODO
    """
    return []

@api.post("/tenant/{tenant_id}/center_arkid/", tags=[_("中心平台")])
def update_center_arkid(request, tenant_id: str):
    """ 更新中心平台配置,TODO
    """
    return []