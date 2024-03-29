from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/bi_systems/", tags=["BI系统"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_bi_systems(request, tenant_id: str):
    """ BI系统列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/bi_systems/{id}/", tags=["BI系统"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_bi_system(request, tenant_id: str, id: str):
    """ 获取BI系统,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/bi_systems/", tags=["BI系统"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_bi_system(request, tenant_id: str):
    """ 创建BI系统,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/bi_systems/{id}/", tags=["BI系统"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_bi_system(request, tenant_id: str, id: str):
    """ 编辑BI系统,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/bi_systems/{id}/", tags=["BI系统"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_bi_system(request, tenant_id: str, id: str):
    """ 删除BI系统,TODO
    """
    return {}


