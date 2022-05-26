from arkid.core.api import api
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
from arkid.core.event import (
    CREATE_AUTO_AUTH_CONFIG,
    DELETE_AUTO_AUTH_CONFIG,
    UPDATE_AUTO_AUTH_CONFIG,
    dispatch_event,
    Event,
)

AutoAuthSchemaIn = AutoAuthExtension.create_composite_config_schema('AutoAuthSchemaIn')


class AutoAuthSchemaOut(ModelSchema):
    class Config:
        model = TenantExtension
        model_fields = ['id', 'settings']

    package: str
    type: str

    @staticmethod
    def resolve_package(obj):
        return obj.extension.package

    @staticmethod
    def resolve_type(obj):
        return obj.extension.type


@api.get(
    "/tenant/{tenant_id}/auto_auths/",
    tags=["自动认证"],
    auth=None,
    response=List[AutoAuthSchemaOut],
)
@paginate
def get_auto_auths(request, tenant_id: str):
    """自动认证列表"""
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, extension__type="auto_auth"
    )
    return settings


@api.get(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthSchemaOut,
)
def get_auto_auth(request, tenant_id: str, id: str):
    """获取自动认证"""
    settings = get_object_or_404(TenantExtension, id=id, tenant=request.tenant)
    return settings


@api.post(
    "/tenant/{tenant_id}/auto_auths/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthSchemaOut,
)
def create_auto_auth(request, tenant_id: str, data: AutoAuthSchemaIn):
    """创建自动认证"""
    tenant = request.tenant
    package = data.package
    config = data.config
    extension = Extension.active_objects.get(package=package)
    extension = import_extension(extension.ext_dir)
    extension_settings = extension.create_tenant_settings(tenant, config.dict())
    dispatch_event(
        Event(
            tag=CREATE_AUTO_AUTH_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )

    return extension_settings


@api.put(
    "/tenant/{tenant_id}/auto_auths/{id}/",
    tags=["自动认证"],
    auth=None,
    response=AutoAuthSchemaOut,
)
def update_auto_auth(request, tenant_id: str, id: str, data: AutoAuthSchemaIn):
    """编辑自动认证"""
    extension_settings = get_object_or_404(
        TenantExtension, id=id, tenant=request.tenant
    )
    tenant = request.tenant
    extension_settings.settings = data.config.dict()
    extension_settings.save()
    dispatch_event(
        Event(
            tag=UPDATE_AUTO_AUTH_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )

    return extension_settings


@api.delete("/tenant/{tenant_id}/auto_auths/{id}/", tags=["自动认证"], auth=None)
def delete_auto_auth(request, tenant_id: str, id: str):
    """删除自动认证"""
    tenant = request.tenant
    extension_settings = get_object_or_404(
        TenantExtension, id=id, tenant=request.tenant
    )
    dispatch_event(
        Event(
            tag=DELETE_AUTO_AUTH_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )
    extension_settings.kill()
    return {'error': ErrorCode.OK.value}
