from arkid.core.api import api
from arkid.core.translation import gettext_default as _

@api.get("/platform_config/", tags=["平台配置"],auth=None)
def get_platform_config(request):
    """ 获取平台配置,TODO
    """
    return {}

@api.post("/platform_config/", tags=["平台配置"],auth=None)
def update_platform_config(request):
    """ 更新平台配置,TODO
    """
    return {}