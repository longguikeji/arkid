#!/usr/bin/env python3
from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.extension.account_life import AccountLifeExtension
from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.extension.models import TenantExtensionConfig, Extension, TenantExtension
from arkid.extension.utils import import_extension
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import ModelSchema
from typing import List
from ninja.pagination import paginate
from arkid.core.event import CREATE_APPROVE_SYSTEM_CONFIG, DELETE_APPROVE_SYSTEM_CONFIG, UPDATE_APPROVE_SYSTEM_CONFIG, dispatch_event, Event
from arkid.core.event import (
    CREATE_ACCOUNT_LIFE_CONFIG,
    UPDATE_ACCOUNT_LIFE_CONFIG,
    DELETE_ACCOUNT_LIFE_CONFIG,
)

ApproveSystemSchemaIn = ApproveSystemExtension.create_composite_config_schema(
    'ApproveSystemSchemaIn'
)


class ApproveSystemSchemaOut(ModelSchema):
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
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=List[ApproveSystemSchemaOut],
)
@paginate
def get_approve_system_list(request, tenant_id: str):
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, extension__type="approve_system"
    )
    return settings


@api.get(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemSchemaOut,
)
def get_approve_system(request, tenant_id: str, id: str):
    settings = get_object_or_404(TenantExtension, id=id, tenant=request.tenant)
    return settings


@api.post(
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemSchemaOut,
)
def create_approve_system(request, tenant_id: str, data: ApproveSystemSchemaIn):
    tenant = request.tenant
    package = data.package
    name = data.name
    type = data.type
    config = data.config
    extension = Extension.active_objects.get(package=package)
    extension = import_extension(extension.ext_dir)
    extension_settings = extension.create_tenant_settings(tenant, config.dict(), type="approve_system")
    dispatch_event(
        Event(
            tag=CREATE_APPROVE_SYSTEM_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )
    return extension_settings


@api.put(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemSchemaOut,
)
def update_approve_system(
    request, tenant_id: str, id: str, data: ApproveSystemSchemaIn
):
    extension_settings = get_object_or_404(
        TenantExtension, id=id, tenant=request.tenant
    )
    tenant = request.tenant
    extension_settings.type = data.type
    extension_settings.settings = data.config.dict()
    extension_settings.save()
    dispatch_event(
        Event(
            tag=UPDATE_APPROVE_SYSTEM_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )

    return extension_settings


@api.delete("/tenant/{tenant_id}/approve_systems/{id}/", tags=["审批系统"], auth=None)
def delete_approve_system(request, tenant_id: str, id: str):
    tenant = request.tenant
    extension_settings = get_object_or_404(
        TenantExtension, id=id, tenant=request.tenant
    )
    dispatch_event(
        Event(
            tag=DELETE_APPROVE_SYSTEM_CONFIG,
            tenant=tenant,
            request=request,
            data=extension_settings,
        )
    )
    extension_settings.delete()
    return {'error': ErrorCode.OK.value}
