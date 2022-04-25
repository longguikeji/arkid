from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/app_protocols/", tags=[_("应用协议")])
def get_app_protocols(request, tenant_id: str):
    """ 应用协议列表,TODO
    """
    return []