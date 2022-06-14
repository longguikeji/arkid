#!/usr/bin/env python3
from arkid.core.api import api, operation
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
from arkid.core.pagenation import CustomPagination
from arkid.core.event import (
    CREATE_APPROVE_SYSTEM_CONFIG,
    DELETE_APPROVE_SYSTEM_CONFIG,
    UPDATE_APPROVE_SYSTEM_CONFIG,
    dispatch_event,
    Event,
)
from api.v1.schema.approve_system import (
    ApproveSystemCreateIn,
    ApproveSystemCreateOut,
    ApproveSystemListItemOut,
    ApproveSystemListOut,
    ApproveSystemOut,
    ApproveSystemUpdateIn,
    ApproveSystemUpdateOut,
    ApproveSystemDeleteOut,
)

from django.db.models import F


@api.get(
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=List[ApproveSystemListItemOut],
)
@operation(ApproveSystemListOut)
@paginate(CustomPagination)
def get_approve_system_list(request, tenant_id: str):
    configs = (
        TenantExtensionConfig.valid_objects.annotate(
            extension_package=F('extension__package'),
            extension_name=F('extension__name'),
        )
        .select_related("extension")
        .filter(tenant_id=tenant_id, extension__type=ApproveSystemExtension.TYPE)
    )

    return configs


@api.get(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemOut,
)
@operation(ApproveSystemOut)
def get_approve_system(request, tenant_id: str, id: str):
    config = (
        TenantExtensionConfig.valid_objects.annotate(package=F('extension__package'))
        .select_related("extension")
        .get(id=id)
    )
    return {"data": config}


@api.post(
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemCreateOut,
)
def create_approve_system(request, tenant_id: str, data: ApproveSystemCreateIn):

    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    extension_config = extension.create_tenant_config(
        request.tenant, data.config.dict(), data.dict()["name"], data.type
    )
    dispatch_event(
        Event(
            tag=CREATE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=extension_config,
        )
    )
    return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemUpdateOut,
)
def update_approve_system(
    request, tenant_id: str, id: str, data: ApproveSystemUpdateIn
):
    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    config = extension.update_tenant_config(
        id, data.config.dict(), data.dict()["name"], data.type
    )
    dispatch_event(
        Event(
            tag=UPDATE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
        )
    )
    return {'error': ErrorCode.OK.value}


@api.delete(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemDeleteOut,
)
@operation(ApproveSystemDeleteOut)
def delete_approve_system(request, tenant_id: str, id: str):
    config = TenantExtensionConfig.active_objects.get(id=id)
    dispatch_event(
        Event(
            tag=DELETE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=config,
        )
    )
    config.delete()
    return {'error': ErrorCode.OK.value}
