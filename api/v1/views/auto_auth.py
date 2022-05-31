from arkid.core.translation import gettext_default as _
from arkid.core.extension.auto_auth import AutoAuthExtension
from arkid.extension.models import TenantExtensionConfig, Extension, TenantExtension
from typing import List
from arkid.core.event import Event
from arkid.extension.utils import import_extension
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import ModelSchema
from ninja.pagination import paginate
from arkid.core.api import api, operation
from arkid.core.pagenation import CustomPagination
from arkid.core.event import (
    CREATE_AUTO_AUTH_CONFIG,
    DELETE_AUTO_AUTH_CONFIG,
    UPDATE_AUTO_AUTH_CONFIG,
    dispatch_event,
    Event,
)
from api.v1.schema.auto_auth import (
    AutoAuthCreateIn,
    AutoAuthCreateOut,
    AutoAuthListItemOut,
    AutoAuthListOut,
    AutoAuthOut,
    AutoAuthUpdateIn,
    AutoAuthUpdateOut,
    AutoAuthDeleteOut,
)


@api.get(
    "/tenant/{tenant_id}/auto_auths/",
    tags=["自动认证"],
    auth=None,
    response=List[AutoAuthListItemOut],
)
@operation(AutoAuthListOut)
@paginate(CustomPagination)
def get_auto_auths(request, tenant_id: str):
    """自动认证列表"""
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, extension__type=AutoAuthExtension.TYPE
    )
    return [
        {
            "id": setting.id.hex,
            "type": setting.extension.type,
            # "name": setting.name,
            "extension_name": setting.extension.name,
            "extension_package": setting.extension.package,
        }
        for setting in settings
    ]


@api.get(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthOut,
)
@operation(AutoAuthOut)
def get_auto_auth(request, tenant_id: str, id: str):
    """获取自动认证"""
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    return {
        "data": {
            "id": setting.id.hex,
            "type": setting.extension.type,
            "package": setting.extension.package,
            "use_platform_config": setting.use_platform_config,
            # "name": setting.name,
            "config": setting.settings,
        }
    }


@api.post(
    "/tenant/{tenant_id}/auto_auths/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthCreateOut,
)
@operation(AutoAuthCreateOut)
def create_auto_auth(request, tenant_id: str, data: AutoAuthCreateIn):
    """创建自动认证"""
    setting = TenantExtension()
    setting.tenant = request.tenant
    setting.extension = Extension.valid_objects.get(package=data.package)
    setting.use_platform_config = data.use_platform_config
    setting.settings = data.config.dict()
    setting.save()
    dispatch_event(
        Event(
            tag=CREATE_AUTO_AUTH_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )

    return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthUpdateOut,
)
def update_auto_auth(request, tenant_id: str, id: str, data: AutoAuthUpdateIn):
    """编辑自动认证"""

    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    setting.settings = data.config.dict()
    setting.use_platform_config = data.use_platform_config
    setting.save()
    dispatch_event(
        Event(
            tag=UPDATE_AUTO_AUTH_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )
    return {'error': ErrorCode.OK.value}


@api.delete(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthDeleteOut,
)
@operation(AutoAuthDeleteOut)
def delete_auto_auth(request, tenant_id: str, id: str):
    """删除自动认证"""
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    dispatch_event(
        Event(
            tag=DELETE_AUTO_AUTH_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )
    setting.kill()
    return {'error': ErrorCode.OK.value}
