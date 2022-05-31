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


@api.get(
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=List[ApproveSystemListItemOut],
)
@operation(ApproveSystemListOut)
@paginate(CustomPagination)
def get_approve_system_list(request, tenant_id: str):
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, extension__type=ApproveSystemExtension.TYPE
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
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemOut,
)
@operation(ApproveSystemOut)
def get_approve_system(request, tenant_id: str, id: str):
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    return {
        "data": {
            "id": setting.id.hex,
            "type": setting.extension.type,
            "package": setting.extension.package,
            "config": setting.settings,
        }
    }


@api.post(
    "/tenant/{tenant_id}/approve_systems/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemCreateOut,
)
def create_approve_system(request, tenant_id: str, data: ApproveSystemCreateIn):
    setting = TenantExtension()
    setting.tenant = request.tenant
    setting.extension = Extension.valid_objects.get(package=data.package)
    setting.settings = data.config.dict()
    setting.save()
    dispatch_event(
        Event(
            tag=CREATE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )
    return {"data": {'error': ErrorCode.OK.value}}


@api.put(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemUpdateOut,
)
def update_approve_system(
    request, tenant_id: str, id: str, data: ApproveSystemUpdateIn
):
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    setting.settings = data.config.dict()
    setting.save()
    dispatch_event(
        Event(
            tag=UPDATE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )
    return {"data": {'error': ErrorCode.OK.value}}


@api.delete(
    "/tenant/{tenant_id}/approve_systems/{id}/",
    tags=["审批系统"],
    auth=None,
    response=ApproveSystemDeleteOut,
)
@operation(ApproveSystemDeleteOut)
def delete_approve_system(request, tenant_id: str, id: str):
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    dispatch_event(
        Event(
            tag=DELETE_APPROVE_SYSTEM_CONFIG,
            tenant=request.tenant,
            request=request,
            data=setting,
        )
    )
    setting.kill()
    return {'error': ErrorCode.OK.value}
