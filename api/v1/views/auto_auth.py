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
from django.db.models import F


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
    configs = (
        TenantExtensionConfig.valid_objects.annotate(
            extension_package=F('extension__package'),
            extension_name=F('extension__name'),
        )
        .select_related("extension")
        .filter(tenant_id=tenant_id, extension__type=AutoAuthExtension.TYPE)
    )

    return configs


@api.get(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthOut,
)
@operation(AutoAuthOut)
def get_auto_auth(request, tenant_id: str, id: str):
    """获取自动认证"""
    config = (
        TenantExtensionConfig.valid_objects.annotate(package=F('extension__package'))
        .select_related("extension")
        .get(id=id)
    )
    return {"data": config}


@api.post(
    "/tenant/{tenant_id}/auto_auths/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthCreateOut,
)
@operation(AutoAuthCreateOut)
def create_auto_auth(request, tenant_id: str, data: AutoAuthCreateIn):
    """创建自动认证"""
    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    extension_config = extension.create_tenant_config(
        request.tenant, data.config.dict(), data.dict()["name"], data.type
    )
    dispatch_event(
        Event(
            tag=CREATE_AUTO_AUTH_CONFIG,
            tenant=request.tenant,
            request=request,
            data=extension_config,
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

    config = TenantExtensionConfig.valid_objects.get(id=id)
    config.config = data.config.dict()
    config.save()
    dispatch_event(
        Event(
            tag=UPDATE_AUTO_AUTH_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
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
    config = TenantExtensionConfig.valid_objects.get(id=id)
    config.delete()
    return {'error': ErrorCode.OK.value}
