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
from pydantic import UUID4


class UserExpirationInSchema(Schema):
    user_id: str = Field(title=_("用户ID"))
    expiration_time: datetime = Field(title=_("过期时间"))


class UserExpirationOutSchema(Schema):
    id: UUID4
    username: str = Field(title=_("用户名"))
    expiration_time: datetime = Field(title=_("过期时间"))


@api.post(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/",
    response=UserExpirationOutSchema,
    tags=['账号生命周期'],
    auth=None,
)
def user_expiration_create(
    request,
    tenant_id: str,
    data: UserExpirationInSchema,
):
    user = User.valid_objects.get(id=data.user_id)
    user_expiration = UserExpiration.valid_objects.filter(target_id=user.id).first()
    if not user_expiration:
        user_expiration = UserExpiration()
        user_expiration.expiration_time = data.expiration_time
        user_expiration.target_id = user.id
    else:
        user_expiration.expiration_time = data.expiration_time
    user_expiration.save()
    return {
        "id": user_expiration.id.hex,
        "username": user.username,
        "expiration_time": user_expiration.expiration_time,
    }


@api.put(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}/",
    response=UserExpirationOutSchema,
    tags=['账号生命周期'],
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
        id=id, target_id__tenant=tenant
    ).first()
    user_expiration.expiration_time = data.expiration_time
    user_expiration.save()
    user = User.valid_objects.get(id=user_expiration.target_id)
    return {
        "id": user_expiration.id.hex,
        "username": user.username,
        "expiration_time": user_expiration.expiration_time,
    }


@api.get(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/",
    response=List[UserExpirationOutSchema],
    tags=['账号生命周期'],
    auth=None,
)
@paginate
def user_expiration_list(
    request,
    tenant_id: str,
):
    tenant = request.tenant
    users = User.expand_objects.filter(tenant=tenant).exclude(
        expiration_time__isnull=True
    )
    result = []
    for user in users:
        user_expiration = UserExpiration.valid_objects.filter(
            target_id=user["id"]
        ).first()
        result.append(
            {
                'id': user_expiration.id.hex,
                'username': user["username"],
                'expiration_time': user_expiration.expiration_time,
            }
        )
    return result


@api.get(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}/",
    response=UserExpirationOutSchema,
    tags=['账号生命周期'],
    auth=None,
)
def get_user_expiration(request, tenant_id: str, id: str):
    tenant = request.tenant
    user_expiration = UserExpiration.valid_objects.filter(
        id=id, target_id__tenant=tenant
    ).first()
    user = User.valid_objects.get(id=user_expiration.target_id)
    return {
        "id": user_expiration.id.hex,
        "username": user.username,
        "expiration_time": user_expiration.expiration_time,
    }


@api.delete(
    "/tenant/{tenant_id}/account_life_arkid/user_expiration/{id}",
    tags=['账号生命周期'],
    auth=None,
)
def delete_user_expiration(request, tenant_id: str, id: str):
    tenant = request.tenant
    user_expiration = User.valid_objects.filter(id=id, tenant=tenant).first()
    if user_expiration:
        user_expiration.expiration_time = None
        user_expiration.save()
    return {'error': ErrorCode.OK.value}
