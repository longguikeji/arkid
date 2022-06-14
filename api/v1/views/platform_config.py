from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.platform_config import *
from arkid.core.models import Platform
from arkid.core.error import ErrorCode

@api.get("/platform_config/",response=PlatformConfigOut, tags=["平台配置"],auth=None)
def get_platform_config(request):
    """ 获取平台配置
    """
    return {"data": Platform.get_config() }

@api.post("/platform_config/",response=ResponseSchema,tags=["平台配置"],auth=None)
def update_platform_config(request,data:PlatformConfigIn):
    """ 更新平台配置,TODO
    """
    config = Platform.get_config()
    for key,value in data.dict().items():
        setattr(config,key,value)
    config.save()
    
    return {"error": ErrorCode.OK.value}