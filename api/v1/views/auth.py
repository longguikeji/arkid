from email import header
from arkid.core.event import register_event, dispatch_event, Event, BEFORE_REFRESH_TOKEN
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token
from arkid.core.error import ErrorCode, ErrorDict
from api.v1.schema.auth import *
from django.http import HttpResponse, JsonResponse
from arkid.core.tasks.celery import dispatch_task

@api.post("/tenant/{tenant_id}/auth/", response=AuthOut, tags=['登录与注册'], auth=None)
@operation(AuthOut, use_id=True)
def auth(request, tenant_id: str, event_tag: str, data: AuthIn):
    tenant = request.tenant
    request_id = request.META.get('HTTP_REQUEST_ID')

    # 认证
    responses = dispatch_event(Event(tag=event_tag, tenant=tenant, request=request, uuid=request_id))
    if not responses:
        return {'error': 'error_code', 'message': '认证插件未启用'}

    useless, (user, useless) = responses[0]
    #befrore_refresh_token
    dispatch_event(Event(tag=BEFORE_REFRESH_TOKEN, tenant=tenant, request=request, uuid=request_id, data={'user':user}))
    # 生成 token
    token = refresh_token(user)
    dispatch_task.delay('async_get_arkstore_access_token', tenant.id.hex, token)
    netloc = request.get_host().split(':')[0]

    is_ip_addr = False
    ip_list = netloc.split('.')
    if len(ip_list) == 4 and ''.join(ip_list).isdigit():
        is_ip_addr = True
    
    domain = ('.'.join(netloc.split('.')[-2:]))
    response = JsonResponse({'error': ErrorCode.OK.value, 'data': {'user': {"id": user.id.hex, "username": user.username}, 'token': token}})
    if is_ip_addr:
        response.set_cookie("arkid_token", token, httponly=True)
    else:
        response.set_cookie("arkid_token", token, domain=domain, httponly=True)

    return response

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