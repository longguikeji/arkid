from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from .schema import *

@api.get(
    "/tenant/{tenant_id}/mine_mobile/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeSchemaOut,
)
def get_account_life(request, tenant_id: str, id: str):
    """获取账号生命周期配置,TODO"""
    config = get_object_or_404(TenantExtensionConfig, id=id, tenant=request.tenant)
    return config