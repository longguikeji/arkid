#!/usr/bin/env python3

from typing import Any, Dict, Optional, List
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.api import api, operation
from arkid.core.models import Tenant, User
from arkid.core.translation import gettext_default as _
from arkid.common.logger import logger
from datetime import datetime
from django.shortcuts import get_object_or_404
from typing import List
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from pydantic import UUID4
from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
)
from arkid.core.models import ApproveAction, ApproveRequest
from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.core.pagenation import CustomPagination


@api.get(
    "/tenant/{tenant_id}/approve_requests/arkid/",
    response=List[ApproveRequestListItemOut],
    tags=['审批请求'],
    auth=None,
)
@operation(ApproveRequestListOut)
@paginate(CustomPagination)
def arkid_approve_request_list(request, tenant_id: str):
    package = 'com.longgui.approve.system.arkid'
    requests = ApproveRequest.valid_objects.filter(
        action__tenant=request.tenant, action__extension__package=package
    )
    return requests


@api.put(
    "/tenant/{tenant_id}/approve_requests/arkid/{id}/",
    # response=ApproveRequestOut,
    tags=['审批请求'],
    auth=None,
)
def arkid_approve_request_process(request, tenant_id: str, id: str, action: str = ''):
    tenant = request.tenant
    approve_request = get_object_or_404(ApproveRequest, id=id, action__tenant=tenant)
    if action == "pass":
        approve_request.status = "pass"
        approve_request.save()
        response = ApproveSystemExtension.restore_request(approve_request)
        logger.info(f'Restore approve request with result: {response}')
        return response
    elif action == "deny":
        approve_request.status = "deny"
        approve_request.save()
        return {'error': ErrorCode.OK.value}
