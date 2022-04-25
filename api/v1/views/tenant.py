from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenants/", tags=[_("租户管理")])
def get_tenant_list(request):
    """ 获取租户管理员行为日志,TODO
    """
    return []