from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.platform_config import *
from django.core.cache import cache

@api.get("/platform_config/",response=PlatformConfigOut, tags=["平台配置"],auth=None)
def get_platform_config(request):
    """ 获取平台配置
    """
    return {"data": {
        "multi_tenant_switch": cache.get("multi_tenant_switch",False)
    }}

@api.post("/platform_config/",response=PlatformConfigOut,tags=["平台配置"],auth=None)
def update_platform_config(request,data:PlatformConfigIn):
    """ 更新平台配置,TODO
    """

    cache.set("multi_tenant_switch",data.multi_tenant_switch)    
    
    return {"data": {
        "multi_tenant_switch": cache.get("multi_tenant_switch",False)
    }}