from arkid.core.event import register_event, dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token
from arkid.core.error import ErrorCode, ErrorDict
from api.v1.schema.auth import *


@api.post("/tenant/{tenant_id}/auth/", response=AuthOut, tags=['登录与注册'], auth=None)
@operation(AuthOut, use_id=True)
def auth(request, tenant_id: str, event_tag: str, data: AuthIn):
    tenant = request.tenant
    request_id = request.META.get('request_id')

    # 认证
    responses = dispatch_event(Event(tag=event_tag, tenant=tenant, request=request, uuid=request_id))
    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}

    useless, (user, useless) = responses[0]

    # 生成 token
    token = refresh_token(user)

    return {'error': ErrorCode.OK.value, 'data': {'user': user, 'token': token}}

@api.post("/tenant/{tenant_id}/reset_password/", response=ResetPasswordOut, tags=['登录与注册'],auth=None)
@operation(ResetPasswordOut, use_id=True)
def reset_passowrd(request, tenant_id: str, event_tag: str, data: ResetPasswordIn):
    tenant = request.tenant
    request_id = request.META.get('request_id')
    
    responses = dispatch_event(Event(tag=event_tag, tenant=tenant, request=request, uuid=request_id))

    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}

    useless, (response, useless) = responses[0]
    
    return response