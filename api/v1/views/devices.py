from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/devices/", tags=[_("设备管理")])
def get_device_list(request, tenant_id: str):
    """ 设备管理列表,TODO
    """
    return []