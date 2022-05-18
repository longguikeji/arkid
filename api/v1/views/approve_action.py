from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from ninja import ModelSchema, Schema
from arkid.core.models import ApproveAction, ApproveRequest
from pydantic import Field
from enum import Enum
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.error import ErrorCode
from typing import List


class METHOD_TYPE(str, Enum):
    GET = _('GET', 'GET')
    POST = _('POST', 'POST')
    DELETE = _('DELETE', 'DELETE')
    PUT = _('PUT', 'PUT')


class ApproveActionSchemaIn(Schema):
    name: str = Field(title=_('Name', '名称'), default='')
    description: str = Field(title=_('Description', '备注'), default='')
    path: str = Field(title=_('Path', '请求路径'))
    method: METHOD_TYPE = Field(title=_('Method', '请求方法'))
    extension_id: str = Field(title=_('Method', '请求方法'))


class ApproveActionSchemaOut(ModelSchema):
    class Config:
        model = ApproveAction
        model_fields = ['id', 'name', 'path', 'method', 'description']

    package: str

    @staticmethod
    def resolve_package(obj):
        if obj.extension:
            return obj.extension.package
        else:
            return ''


@api.get(
    "/tenant/{tenant_id}/approve_actions/",
    tags=["审批动作"],
    auth=None,
    response=List[ApproveActionSchemaOut],
)
def get_approve_actions(request, tenant_id: str):
    """审批动作列表,TODO"""
    tenant = request.tenant
    actions = ApproveAction.valid_objects.filter(tenant=tenant)
    return actions


@api.get(
    operation_id="",
    path="/tenant/{tenant_id}/approve_actions/{id}/",
    tags=["审批动作"],
    auth=None,
    response=ApproveActionSchemaOut,
)
def get_approve_action(request, tenant_id: str, id: str):
    """获取审批动作,TODO"""
    tenant = request.tenant
    action = ApproveAction.valid_objects.filter(tenant=tenant, id=id).first()
    if not action:
        return {'error': ErrorCode.APPROVE_ACTION_NOT_EXISTS.value}
    else:
        return action


@api.post("/tenant/{tenant_id}/approve_actions/", tags=["审批动作"], auth=None)
def create_approve_action(request, tenant_id: str, data: ApproveActionSchemaIn):
    """创建审批动作,TODO"""
    tenant = request.tenant
    name = data.name
    description = data.description
    path = data.path
    method = data.method
    extension_id = data.extension_id
    extension = Extension.valid_objects.get(id=extension_id)
    action = ApproveAction.valid_objects.filter(
        path=path, method=method, extension=extension, tenant=tenant
    ).first()
    if action:
        return {'error': ErrorCode.APPROVE_ACTION_DUPLICATED.value}
    else:
        action = ApproveAction.valid_objects.create(
            name=name,
            description=description,
            path=path,
            method=method,
            extension=extension,
            tenant=tenant,
        )
        return {'error': ErrorCode.OK.value}


@api.put("/tenant/{tenant_id}/approve_actions/{id}/", tags=["审批动作"], auth=None)
def update_approve_action(
    request, tenant_id: str, id: str, data: ApproveActionSchemaIn
):
    """编辑审批动作,TODO"""
    tenant = request.tenant
    name = data.name
    description = data.description
    path = data.path
    method = data.method
    extension_id = data.extension_id
    extension = Extension.valid_objects.get(id=extension_id)
    action = ApproveAction.valid_objects.filter(tenant=tenant, id=id).first()
    if not action:
        return {'error': ErrorCode.APPROVE_ACTION_NOT_EXISTS.value}
    else:
        action.name = name
        action.description = description
        action.path = path
        action.method = method
        action.extension = extension
        action.save()
        return {'error': ErrorCode.OK.value}


@api.delete("/tenant/{tenant_id}/approve_actions/{id}/", tags=["审批动作"], auth=None)
def delete_approve_action(request, tenant_id: str, id: str):
    """删除审批动作,TODO"""
    tenant = request.tenant
    action = ApproveAction.valid_objects.filter(tenant=tenant, id=id).first()
    if not action:
        return {'error': ErrorCode.APPROVE_ACTION_NOT_EXISTS.value}
    else:
        action.delete()
        return {'error': ErrorCode.OK.value}
