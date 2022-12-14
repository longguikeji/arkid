import os
import requests
from django.conf import settings
from arkid.config import get_app_config
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from api.v1.schema.platform_config import *
from arkid.core.models import Platform
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.event import Event, dispatch_event, SET_FRONTEND_URL, UPDATE_LOCAL_ARKID_VERSION


@api.get("/platform_config/",response=PlatformConfigOut, tags=["平台配置"])
@operation(roles=[PLATFORM_ADMIN])
def get_platform_config(request):
    """ 获取平台配置
    """
    return {"data": Platform.get_config() }

@api.get("/platform_config_with_no_permission/",response=PlatformConfigOut, tags=["平台配置"],auth=None)
@operation()
def get_platform_config_with_no_permission(request):
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
        # if key == "frontend_url":
            # from urllib.parse import urlparse
            # ret = urlparse(value)
            # if ret.scheme in ["http","https"] and ret.netloc:
            #     pass
            # else:
            #     continue
        
        setattr(config,key,value)
    config.save()
    
    return {"error": ErrorCode.OK.value,"message":_("配置成功")}

@api.get("/frontend_url/",response=FrontendUrlOut, tags=["平台配置"],auth=None)
def get_frontend_url(request):
    """ 获取ArkId访问地址
    """
    config = Platform.get_config()
    return SuccessDict(
        data={
            "db_url": config.frontend_url,
            "toml_url": get_app_config().get_frontend_host(),
            "dev": False if os.environ.get('K8SORDC') else True
        }
    )


@api.post("/frontend_url/",response=FrontendUrlOut, tags=["平台配置"],auth=None)
def set_frontend_url(request, data:FrontendUrlSchemaIn):
    """ 设置ArkId访问地址
    """
    config = Platform.get_config()
    if not os.environ.get('K8SORDC') or config.frontend_url is not None:
        return ErrorDict(
            ErrorCode.CAN_NOT_SET_FRONTEND_URL
        )
    url = data.dict().get("url", "")
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
    
    from arkid import settings
    if config.frontend_url:
        settings.CSRF_TRUSTED_ORIGINS.append(config.frontend_url)

    dispatch_event(
        Event(
            tag=SET_FRONTEND_URL,
            tenant=request.tenant,
            data={},
        )
    )
    
    return SuccessDict(
        data={
            "db_url": config.frontend_url,
            "toml_url": get_app_config().get_frontend_host(),
            "dev": False if os.environ.get('K8SORDC') else True
        }
    )


@api.get("/version/",response=VersionOut, tags=["平台配置"])
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_version(request, local_version=None):
    """ 获取ArkId版本
    """
    version = os.environ.get('ARKID_VERSION', '')
    update_url = settings.UPDATE_URL

    if settings.IS_CENTRAL_ARKID:
        if local_version:
            dispatch_event(
                Event(
                    tag=UPDATE_LOCAL_ARKID_VERSION,
                    tenant=request.tenant,
                    request=request,
                    data = {"local_version": local_version}
                )
            )
        new_version = ''
        update_available = False
    else:
        try:
            from arkid.common.arkstore import get_saas_token
            token = request.user.auth_token
            tenant = request.tenant
            saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(tenant, token)
            arkid_saas_version_url = settings.ARKID_SAAS_URL + '/api/v1/version/'
            headers = {'Authorization': f'Token {saas_token}'}
            params = {"local_version": version}
            resp = requests.get(arkid_saas_version_url, params=params, headers=headers, timeout=5).json()
            new_version = resp.get('data', {}).get('version', '')
            if version and new_version and version < new_version:
                update_available = True
            else:
                update_available = False
        except:
            new_version = ''
            update_available = False

    return SuccessDict(
        data={
            "version": version,
            "update_available": update_available,
            "new_version": new_version,
            "update_url": update_url
        }
    )


@api.get("/restart/", tags=["平台配置"])
@operation(roles=[PLATFORM_ADMIN])
def restart(request):
    from arkid.extension.utils import restart_arkid
    restart_arkid()


@api.delete("/restart/", tags=["平台配置"])
@operation(roles=[PLATFORM_ADMIN])
def restart(request):
    from arkid.extension.utils import restart_arkid
    restart_arkid()
