from enum import Enum
from logging.config import listen
from typing import Any, Dict, Optional, List
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import register_event, dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.models import Tenant, ExpiringToken
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token

class AuthTenantSchema(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ['uuid', 'name', 'slug', 'icon']
        # validate = False


class AuthOut(Schema):
    data: Dict[str, Optional[Any]]
    tenant: AuthTenantSchema


@api.post("/auth/", response=AuthOut, auth=None)
@operation(AuthOut, use_uuid=True)
def auth(request, data: Any):
    tenant_uuid = data.tenant
    tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
    request.tenant = tenant

    request_uuid = request.Meta.get('request_uuid')

    # 认证
    responses = dispatch_event(Event(tag=data.tag, tenant=tenant, request=request, uuid=request_uuid))
    if len(responses) < 1:
        return {'error': 'error_code', 'message': '认证插件未启用'}

    response = responses[0]
    _, (response, _) = response
    user = response.get('user')
    
    # 生成 token
    token = refresh_token(user)

    return {'data': {'token': token, 'user': user.uuid.hex}}
