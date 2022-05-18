#!/usr/bin/env python3

from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from ninja import ModelSchema, Schema
from arkid.core.models import ApproveAction, ApproveRequest
from pydantic import Field
from enum import Enum
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.error import ErrorCode
from typing import List
from django.shortcuts import get_object_or_404
from arkid.core.extension.approve_system import ApproveSystemExtension
from ninja.pagination import paginate


class ApproveRequestOut(ModelSchema):
    class Config:
        model = ApproveRequest
        model_fields = ['id', 'status']

    username: str
    path: str
    method: str

    @staticmethod
    def resolve_username(obj):
        return obj.user.username

    @staticmethod
    def resolve_path(obj):
        return obj.action.path

    @staticmethod
    def resolve_method(obj):
        return obj.action.method


@api.get(
    "/tenant/{tenant_id}/approve_system/system_approve_requests/",
    response=List[ApproveRequestOut],
    tags=['审批请求'],
    auth=None,
)
@paginate
def system_approve_request_list(request, tenant_id: str, package: str=""):
    tenant = request.tenant
    requests = ApproveRequest.valid_objects.filter(
        action__extension__type="approve_system", action__tenant=tenant
    )
    if package:
        requests = requests.filter(action__extension__package=package)
    return requests


@api.put(
    "/tenant/{tenant_id}/approve_system/approve_requests/{request_id}/",
    # response=ApproveRequestOut,
    tags=['审批请求'],
    auth=None,
)
def approve_request_process(request, tenant_id: str, request_id: str, action: str = ''):
    tenant = request.tenant
    approve_request = get_object_or_404(
        ApproveRequest, id=request_id, action__tenant=tenant
    )
    if action == "pass":
        approve_request.status = "pass"
        approve_request.save()
        response = ApproveSystemExtension.restore_request(approve_request)
        return response
    elif action == "deny":
        approve_request.status = "deny"
        approve_request.save()
        return {'error': ErrorCode.OK.value}
