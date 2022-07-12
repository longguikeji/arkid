from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from ninja import ModelSchema, Schema
from arkid.core.models import ApproveAction, ApproveRequest
from pydantic import Field
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.error import ErrorCode, ErrorDict
from typing import List
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from api.v1.schema.approve_action import (
    ApproveActionCreateIn,
    ApproveActionCreateOut,
    ApproveActionListItemOut,
    ApproveActionOut,
    ApproveActionUpdateIn,
    ApproveActionUpdateOut,
    ApproveActionDeleteOut,
)


@api.get(
    "/tenant/{tenant_id}/approve_actions/",
    tags=["审批动作"],
    response=List[ApproveActionListItemOut],
)
@operation(List[ApproveActionListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_approve_actions(request, tenant_id: str):
    """审批动作列表"""
    tenant = request.tenant
    actions = ApproveAction.valid_objects.filter(tenant=tenant)
    return actions


@api.get(
    path="/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    response=ApproveActionOut,
)
@operation(ApproveActionOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_approve_action(request, tenant_id: str, id: str):
    """获取审批动作"""
    tenant = request.tenant
    action = ApproveAction.valid_objects.filter(tenant=tenant, id=id).first()
    return {"data": action}


@api.post(
    "/tenant/{tenant_id}/approve_actions/",
    tags=["审批动作"],
    response=ApproveActionCreateOut,
)
@operation(ApproveActionOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_approve_action(request, tenant_id: str, data: ApproveActionCreateIn):
    """创建审批动作"""
    extension = Extension.valid_objects.get(id=data.extension_id)
    action = ApproveAction.valid_objects.filter(
        path=data.path, method=data.method, extension=extension, tenant=request.tenant
    ).first()
    if action:
        return ErrorDict(ErrorCode.APPROVE_ACTION_DUPLICATED)
    else:
        action = ApproveAction.valid_objects.create(
            name=data.name,
            description=data.description,
            path=data.path,
            method=data.method,
            extension=extension,
            tenant=request.tenant,
        )
        return ErrorDict(ErrorCode.OK)


@api.put(
    "/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    response=ApproveActionUpdateOut,
)
@operation(ApproveActionUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_approve_action(
    request, tenant_id: str, id: str, data: ApproveActionUpdateIn
):
    """编辑审批动作"""
    extension = Extension.valid_objects.get(id=data.extension_id)
    action = ApproveAction.valid_objects.filter(tenant=request.tenant, id=id).first()
    if not action:
        return ErrorDict(ErrorCode.APPROVE_ACTION_NOT_EXISTS)
    else:
        action.name = data.name
        action.description = data.description
        action.path = data.path
        action.method = data.method
        action.extension = extension
        action.save()
        return ErrorDict(ErrorCode.OK)


@api.delete(
    "/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    response=ApproveActionDeleteOut,
)
@operation(ApproveActionDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_approve_action(request, tenant_id: str, id: str):
    """删除审批动作"""
    action = ApproveAction.valid_objects.filter(tenant=request.tenant, id=id).first()
    if not action:
        return ErrorDict(ErrorCode.APPROVE_ACTION_NOT_EXISTS)
    else:
        action.delete()
        return ErrorDict(ErrorCode.OK)


class ApproveSystemExtensionListOut(ModelSchema):
    class Config:
        model = Extension
        model_fields = [
            "id",
            "name",
            "type",
            "package",
            "labels",
            "version",
            "is_active",
            "is_allow_use_platform_config",
        ]


@api.get(
    "/tenant/{tenant_id}/approve_system_extensions/",
    response=List[ApproveSystemExtensionListOut],
    tags=['审批动作'],
)
@operation(List[ApproveSystemExtensionListOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def list_approve_system_extensions(request, tenant_id: str):
    """获取审批系统插件列表"""
    qs = Extension.active_objects.filter(type='approve_system').all()
    return qs
