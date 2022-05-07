from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.extension.utils import import_extension
from arkid.extension.models import TenantExtensionConfig, Extension, TenantExtension
from uuid import UUID
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import Schema, ModelSchema
from typing import List
from ninja.pagination import paginate

ThirdAuthConfigSchemaIn = ExternalIdpExtension.create_composite_config_schema(
    'ThirdAuthConfigSchemaIn'
)


class ThirdAuthConfigSchemaOut(ModelSchema):
    class Config:
        model = TenantExtension
        model_fields = ['id', 'type', 'settings']

    package: str

    @staticmethod
    def resolve_package(obj):
        return obj.extension.package


@api.get(
    "/tenant/{tenant_id}/third_auths/",
    tags=["第三方认证"],
    auth=None,
    response=List[ThirdAuthConfigSchemaOut],
)
@paginate
def get_third_auths(request, tenant_id: str):
    """第三方认证列表,TODO"""
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, type="external_idp"
    )
    return settings


@api.get(
    "/tenant/{tenant_id}/third_auths/{id}/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthConfigSchemaOut,
)
def get_third_auth(request, tenant_id: str, id: str):
    """获取第三方认证,TODO"""
    config = get_object_or_404(TenantExtension, id=id, tenant=request.tenant)
    return config


@api.post(
    "/tenant/{tenant_id}/third_auths/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthConfigSchemaOut,
)
def create_third_auth(request, tenant_id: str, data: ThirdAuthConfigSchemaIn):
    """创建第三方认证,TODO"""
    tenant = request.tenant
    package = data.package
    type = data.type
    config = data.config
    extension = Extension.active_objects.get(package=package)
    extension = import_extension(extension.ext_dir)
    extension_settings = extension.create_tenant_settings(
        tenant, config.dict(), type=type
    )
    return extension_settings


@api.put("/tenant/{tenant_id}/third_auths/{id}/", tags=["第三方认证"], auth=None)
def update_third_auth(request, tenant_id: str, id: str, data: ThirdAuthConfigSchemaIn):
    """编辑第三方认证,TODO"""
    extension_settings = get_object_or_404(
        TenantExtension, id=id, tenant=request.tenant
    )
    extension_settings.package = data.package
    # extension_settings.name = data.name
    extension_settings.type = data.type
    extension_settings.settings = data.config
    extension_settings.save()

    return extension_settings


@api.delete("/tenant/{tenant_id}/third_auths/{id}/", tags=["第三方认证"], auth=None)
def delete_third_auth(request, tenant_id: str, id: str):
    """删除第三方认证,TODO"""
    extension_config = get_object_or_404(TenantExtension, id=id, tenant=request.tenant)
    extension_config.delete()
    return {'error': ErrorCode.OK.value}
