from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from ninja import ModelSchema, Schema
from arkid.core.models import ApproveAction, ApproveRequest
from pydantic import Field
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.error import ErrorCode
from typing import List
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from api.v1.schema.approve_action import (
    ApproveActionCreateIn,
    ApproveActionCreateOut,
    ApproveActionListItemOut,
    ApproveActionListOut,
    ApproveActionOut,
    ApproveActionUpdateIn,
    ApproveActionUpdateOut,
    ApproveActionDeleteOut,
)


@api.get(
    "/tenant/{tenant_id}/approve_actions/",
    tags=["审批动作"],
    auth=None,
    response=List[ApproveActionListItemOut],
)
@operation(ApproveActionListOut)
@paginate(CustomPagination)
def get_approve_actions(request, tenant_id: str):
    """审批动作列表"""
    tenant = request.tenant
    actions = ApproveAction.valid_objects.filter(tenant=tenant)
    return actions


@api.get(
    operation_id="",
    path="/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    auth=None,
    response=ApproveActionOut,
)
def get_approve_action(request, tenant_id: str, id: str):
    """获取审批动作"""
    tenant = request.tenant
    action = ApproveAction.valid_objects.filter(tenant=tenant, id=id).first()
    return {"data": action}


@api.post(
    "/tenant/{tenant_id}/approve_actions/",
    tags=["审批动作"],
    auth=None,
    response=ApproveActionCreateOut,
)
def create_approve_action(request, tenant_id: str, data: ApproveActionCreateIn):
    """创建审批动作"""
    extension = Extension.valid_objects.get(id=data.extension_id)
    action = ApproveAction.valid_objects.filter(
        path=data.path, method=data.method, extension=extension, tenant=request.tenant
    ).first()
    if action:
        return {'error': ErrorCode.APPROVE_ACTION_DUPLICATED.value}
    else:
        action = ApproveAction.valid_objects.create(
            name=data.name,
            description=data.description,
            path=data.path,
            method=data.method,
            extension=extension,
            tenant=request.tenant,
        )
        return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    auth=None,
    response=ApproveActionUpdateOut,
)
def update_approve_action(
    request, tenant_id: str, id: str, data: ApproveActionUpdateIn
):
    """编辑审批动作"""
    extension = Extension.valid_objects.get(id=data.extension_id)
    action = ApproveAction.valid_objects.filter(tenant=request.tenant, id=id).first()
    if not action:
        return {'error': ErrorCode.APPROVE_ACTION_NOT_EXISTS.value}
    else:
        action.name = data.name
        action.description = data.description
        action.path = data.path
        action.method = data.method
        action.extension = extension
        action.save()
        return {'error': ErrorCode.OK.value}


@api.delete(
    "/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    auth=None,
    response=ApproveActionDeleteOut,
)
@operation(ApproveActionDeleteOut)
def delete_approve_action(request, tenant_id: str, id: str):
    """删除审批动作"""
    action = ApproveAction.valid_objects.filter(tenant=request.tenant, id=id).first()
    if not action:
        return {'error': ErrorCode.APPROVE_ACTION_NOT_EXISTS.value}
    else:
        action.delete()
        return {'error': ErrorCode.OK.value}
