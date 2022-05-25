#!/usr/bin/env python3

from email import message
from typing import Any, Dict, Optional, List
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.api import api, operation
from arkid.core.models import Tenant, User
from arkid.core.translation import gettext_default as _
from arkid.core.event import CREATE_LOGIN_PAGE_AUTH_FACTOR, CREATE_LOGIN_PAGE_RULES
from arkid.common.logger import logger
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import UserExpiration
from typing import List
from ninja.pagination import paginate
from arkid.core.error import ErrorCode


class UserExpirationInSchema(Schema):
    user_id: str
    expiration_time: datetime


class UserExpirationOutSchema(Schema):
    id: str
    username: str
    expiration_time: datetime


@api.post(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/",
    response=UserExpirationOutSchema,
    tags=['用户'],
    auth=None,
)
def user_expiration_create(
    request,
    tenant_id: str,
    data: UserExpirationInSchema,
):
    tenant = request.tenant
    user_expiration = UserExpiration.valid_objects.filter(
        user__id=data.user_id, user__tenant=tenant
    ).first()
    if not user_expiration:
        user = User.valid_objects.get(id=data.user_id)
        user_expiration = UserExpiration.valid_objects.create(
            user=user, expiration_time=data.expiration_time
        )
    else:
        user_expiration.expiration_time = data.expiration_time
        user_expiration.is_del = False
        user_expiration.save()
    return {
        "id": user_expiration.id.hex,
        "username": user_expiration.user.username,
        "expiration_time": user_expiration.expiration_time,
    }


@api.put(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}",
    response=UserExpirationOutSchema,
    tags=['用户'],
    auth=None,
)
def user_expiration_update(
    request,
    tenant_id: str,
    id: str,
    data: UserExpirationInSchema,
):
    tenant = request.tenant
    user_expiration = UserExpiration.valid_objects.filter(
        id=id, user__tenant=tenant
    ).first()
    user_expiration.expiration_time = data.expiration_time
    user_expiration.save()
    return {
        "id": user_expiration.id.hex,
        "username": user_expiration.user.username,
        "expiration_time": user_expiration.expiration_time,
    }


@api.get(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/",
    response=List[UserExpirationOutSchema],
    tags=['用户'],
    auth=None,
)
@paginate
def user_expiration_list(
    request,
    tenant_id: str,
):
    tenant = request.tenant
    user_expirations = User.valid_objects.filter(tenant=tenant).exclude(
        expiration_time__isnull=True
    )
    return user_expirations


@api.get(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}",
    response=UserExpirationOutSchema,
    tags=['用户'],
    auth=None,
)
def get_user_expiration(request, tenant_id: str, id: str):
    tenant = request.tenant
    user_expiration = UserExpiration.valid_objects.filter(
        id=id, user__tenant=tenant
    ).first()
    return user_expiration


@api.delete(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}",
    tags=['用户'],
    auth=None,
)
def delete_user_expiration(request, tenant_id: str, id: str):
    tenant = request.tenant
    user_expiration = UserExpiration.valid_objects.filter(
        id=id, user__tenant=tenant
    ).first()
    if user_expiration:
        user_expiration.delete()
    return {'error': ErrorCode.OK.value}
