#!/usr/bin/env python3

from arkid.core.api import api, operation
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
from arkid.core.pagenation import CustomPagination
from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
)


@api.get(
    "/tenant/{tenant_id}/approve_requests/",
    response=List[ApproveRequestListItemOut],
    tags=['审批请求'],
    auth=None,
)
@operation(ApproveRequestListOut)
@paginate(CustomPagination)
def approve_request_list(
    request, tenant_id: str, package: str = "", is_approved: str = ""
):
    tenant = request.tenant
    requests = ApproveRequest.valid_objects.filter(action__tenant=tenant)
    if package:
        requests = requests.filter(action__extension__package=package)
    if is_approved == "true":
        requests = requests.exclude(status="wait")
    elif is_approved == "false":
        requests = requests.filter(status="wait")
    return requests
