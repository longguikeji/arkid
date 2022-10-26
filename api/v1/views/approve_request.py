#!/usr/bin/env python3

from ninja import Query
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from ninja import ModelSchema, Schema
from arkid.core.models import ApproveAction, ApproveRequest
from pydantic import Field
from enum import Enum
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.error import ErrorCode, ErrorDict
from typing import List
from django.shortcuts import get_object_or_404
from arkid.core.extension.approve_system import ApproveSystemExtension
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
    ApproveRequestListQueryIn,
)


@api.get(
    "/tenant/{tenant_id}/approve_requests/",
    response=List[ApproveRequestListItemOut],
    tags=['审批请求'],
)
@operation(List[ApproveRequestListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def approve_request_list(
    request, tenant_id: str, query_data:ApproveRequestListQueryIn=Query(...)
):
    tenant = request.tenant
    requests = ApproveRequest.valid_objects.filter(tenant=tenant)
    if query_data.package:
        requests = requests.filter(action__extension__package=query_data.package)
    if query_data.username:
        requests = requests.filter(user__username__icontains=query_data.username)
    if query_data.is_approved == "true":
        requests = requests.exclude(status="wait")
    elif query_data.is_approved == "false":
        requests = requests.filter(status="wait")
    return requests
