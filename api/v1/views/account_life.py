from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.extension.account_life import AccountLifeExtension
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.extension.utils import import_extension
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import ModelSchema
from typing import List
from ninja.pagination import paginate
from arkid.core.event import dispatch_event, Event
from arkid.core.event import (
    CREATE_ACCOUNT_LIFE_CONFIG,
    UPDATE_ACCOUNT_LIFE_CONFIG,
    DELETE_ACCOUNT_LIFE_CONFIG,
)

AccountLifeSchemaIn = AccountLifeExtension.create_composite_config_schema(
    'AccountLifeSchemaIn'
)


class AccountLifeSchemaOut(ModelSchema):
    class Config:
        model = TenantExtensionConfig
        model_fields = ['id', 'name', 'type', 'config']

    package: str

    @staticmethod
    def resolve_package(obj):
        return obj.extension.package


@api.get(
    "/tenant/{tenant_id}/account_lifes/",
    tags=["账号生命周期"],
    auth=None,
    response=List[AccountLifeSchemaOut],
)
@paginate
def get_account_life_list(request, tenant_id: str):
    """账号生命周期配置列表,TODO"""
    configs = TenantExtensionConfig.valid_objects.filter(
        tenant_id=tenant_id, extension__type="account_life"
    )
    return configs


@api.get(
    "/tenant/{tenant_id}/account_lifes/{id}/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeSchemaOut,
)
def get_account_life(request, tenant_id: str, id: str):
    """获取账号生命周期配置,TODO"""
    config = get_object_or_404(TenantExtensionConfig, id=id, tenant=request.tenant)
    return config


@api.post(
    "/tenant/{tenant_id}/account_lifes/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeSchemaOut,
)
def create_account_life(request, tenant_id: str, data: AccountLifeSchemaIn):
    """创建账号生命周期配置,TODO"""
    tenant = request.tenant
    package = data.package
    name = data.name
    type = data.type
    config = data.config
    extension = Extension.active_objects.get(package=package)
    extension = import_extension(extension.ext_dir)
    extension_config = extension.create_tenant_config(
        tenant, config.dict(), name=name, type=type
    )
    dispatch_event(
        Event(
            tag=CREATE_ACCOUNT_LIFE_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_config,
        )
    )
    return extension_config


@api.put(
    "/tenant/{tenant_id}/account_lifes/{id}/",
    tags=["账号生命周期"],
    auth=None,
    response=AccountLifeSchemaOut,
)
def update_account_life(request, tenant_id: str, id: str, data: AccountLifeSchemaIn):
    """编辑账号生命周期配置,TODO"""
    extension_config = get_object_or_404(
        TenantExtensionConfig, id=id, tenant=request.tenant
    )
    tenant = request.tenant
    extension_config.name = data.name
    extension_config.type = data.type
    extension_config.config = data.config.dict()
    extension_config.save()
    dispatch_event(
        Event(
            tag=UPDATE_ACCOUNT_LIFE_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_config,
        )
    )

    return extension_config


@api.delete("/tenant/{tenant_id}/account_lifes/{id}/", tags=["账号生命周期"], auth=None)
def delete_account_life(request, tenant_id: str, id: str):
    """删除账号生命周期配置,TODO"""
    tenant = request.tenant
    extension_config = get_object_or_404(
        TenantExtensionConfig, id=id, tenant=request.tenant
    )
    dispatch_event(
        Event(
            tag=DELETE_ACCOUNT_LIFE_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_config,
        )
    )
    extension_config.delete()
    return {'error': ErrorCode.OK.value}
