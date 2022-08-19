from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from api.v1.schema.platform_config import *
from arkid.core.models import Platform
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict

@api.get("/platform_config/",response=PlatformConfigOut, tags=["平台配置"])
@operation(roles=[PLATFORM_ADMIN])
def get_platform_config(request):
    """ 获取平台配置
    """
    return {"data": Platform.get_config() }

@api.post("/platform_config/",response=ResponseSchema,tags=["平台配置"])
@operation(roles=[PLATFORM_ADMIN])
def update_platform_config(request,data:PlatformConfigIn):
    """ 更新平台配置,TODO
    """
    config = Platform.get_config()
    for key,value in data.dict().items():
        
        # 添加对前端url的合法性校验
        if key == "frontend_url":
            from urllib.parse import urlparse
            ret = urlparse(value)
            if ret.scheme in ["http","https"] and ret.netloc:
                pass
            else:
                continue
        
        setattr(config,key,value)
    config.save()
    
    return {"error": ErrorCode.OK.value}

@api.get("/frontend_url/",response=FrontendUrlOut, tags=["平台配置"],auth=None)
def get_frontend_url(request):
    """ 获取ArkId访问地址
    """
    config = Platform.get_config()
    return SuccessDict(
        data={
            "url": config.frontend_url
        }
    )


@api.post("/frontend_url/",response=FrontendUrlOut, tags=["平台配置"],auth=None)
def set_frontend_url(request,data:FrontendUrlSchema):
    """ 获取ArkId访问地址
    """
    config = Platform.get_config()
    url = data.dict().get("url")
    from urllib.parse import urlparse
    ret = urlparse(url)
    if ret.scheme in ["http","https"] and ret.netloc:
        pass
    else:
        return ErrorDict(
            ErrorCode.INVALID_FRONTEND_URL
        )
    config.frontend_url = url
    config.save()
    
    return SuccessDict(
        data={
            "url": config.frontend_url
        }
    )
