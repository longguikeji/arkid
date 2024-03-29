from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from webhook.models import Webhook, WebhookEvent, WebhookTriggerHistory
from arkid.core.error import ErrorCode, ErrorDict
from typing import List
from ninja.pagination import paginate
from ninja import ModelSchema, Schema
from pydantic import Field
import json
import requests
from api.v1.schema.webhook import (
    WebhookCreateIn,
    WebhookCreateOut,
    WebhookDeleteOut,
    WebhookListItemOut,
    WebhookListOut,
    WebhookOut,
    WebhookUpdateIn,
    WebhookUpdateOut,
    WebhookHistoryListItemOut,
    WebhookHistoryListOut,
    WebhookHistoryOut,
    WebhookHistoryRetryOut,
    WebhookHistoryDeleteOut,
)
from arkid.core.pagenation import CustomPagination


@api.get(
    "/tenant/{tenant_id}/webhooks/",
    tags=["Webhook"],
    response=List[WebhookListItemOut],
)
@operation(List[WebhookListItemOut],roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_webhooks(request, tenant_id: str):
    tenant = request.tenant
    webhooks = Webhook.valid_objects.filter(tenant=tenant)
    return webhooks


@api.get(
    "/tenant/{tenant_id}/webhooks/{id}/",
    tags=["Webhook"],
    response=WebhookOut,
)
@operation(WebhookOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_webhook(request, tenant_id: str, id: str):
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    events = [event.event_type for event in webhook.events_set.all()]
    return {
        "data": {
            "name": webhook.name,
            "url": webhook.url,
            "secret": webhook.secret,
            "events": events,
        }
    }


@api.post(
    "/tenant/{tenant_id}/webhooks/",
    tags=["Webhook"],
    response=WebhookCreateOut,
)
@operation(WebhookCreateOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_webhook(request, tenant_id: str, data: WebhookCreateIn):
    tenant = request.tenant
    name = data.name
    url = data.url
    secret = data.secret
    events = data.events
    webhook = Webhook.valid_objects.create(
        tenant=tenant, name=name, url=url, secret=secret
    )
    for event in events:
        webhook_event, _ = WebhookEvent.valid_objects.update_or_create(event_type=event)
        webhook.events_set.add(webhook_event)
    return webhook


@api.put(
    "/tenant/{tenant_id}/webhooks/{id}/",
    tags=["Webhook"],
    response=WebhookUpdateOut,
)
@operation(WebhookUpdateOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_webhook(request, tenant_id: str, id: str, data: WebhookUpdateIn):
    tenant = request.tenant
    name = data.name
    url = data.url
    secret = data.secret
    events = data.events
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    webhook.events_set.clear()
    webhook.name = name
    webhook.url = url
    webhook.secret = secret
    for event in events:
        webhook_event, _ = WebhookEvent.valid_objects.update_or_create(event_type=event)
        webhook.events_set.add(webhook_event)
    webhook.save()
    return webhook


@api.delete(
    "/tenant/{tenant_id}/webhooks/{id}/",
    tags=["Webhook"],
    response=WebhookDeleteOut,
)
@operation(WebhookDeleteOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_webhook(request, tenant_id: str, id: str):
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    else:
        webhook.delete()
        return ErrorDict(ErrorCode.OK)


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/",
    tags=["Webhook"],
    response=List[WebhookHistoryListItemOut],
)
@operation(List[WebhookHistoryListItemOut],roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_webhook_histories(request, tenant_id: str, webhook_id: str):
    """获取Webhook历史记录列表"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    histories = webhook.history_set.all().filter(is_del=False)
    return histories


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/",
    tags=["Webhook"],
    response=WebhookHistoryOut,
)
@operation(WebhookHistoryOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """获取Webhook历史记录"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    history = WebhookTriggerHistory.valid_objects.filter(webhook=webhook, id=id).first()
    if not history:
        return ErrorDict(ErrorCode.WEBHOOK_HISTORY_NOT_EXISTS)
    return {"data": history}


@api.delete(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/",
    tags=["Webhook"],
    response=WebhookHistoryDeleteOut,
)
@operation(WebhookHistoryDeleteOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """删除Webhook历史记录"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    history = WebhookTriggerHistory.valid_objects.filter(webhook=webhook, id=id).first()
    if not history:
        return ErrorDict(ErrorCode.WEBHOOK_HISTORY_NOT_EXISTS)
    history.delete()
    return ErrorDict(ErrorCode.OK)


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/retry/",
    tags=["Webhook"],
    response=WebhookHistoryRetryOut,
)
@operation(WebhookHistoryRetryOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def retry_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """重试webhook历史记录"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return ErrorDict(ErrorCode.WEBHOOK_NOT_EXISTS)
    history = WebhookTriggerHistory.valid_objects.filter(webhook=webhook, id=id).first()
    if not history:
        return ErrorDict(ErrorCode.WEBHOOK_HISTORY_NOT_EXISTS)

    webhook = history.webhook
    url = webhook.url
    request_data = json.loads(history.request)
    request_headers = request_data.get('headers')
    request_body = request_data.get('body')
    response = None
    try:
        response = requests.post(url, request_body, headers=request_headers, timeout=3)
        response.raise_for_status()
    except Exception as exc:
        if response:
            status_code = response.status_code
        else:
            status_code = None
        history.status = 'failed'
        response_data = json.dumps({'status_code': status_code, 'body': str(exc)})
        history.response = response_data
        history.save()
    else:
        history.status = 'success'
        history.response = json.dumps(
            {
                'status_code': response.status_code,
                'response': response.text,
            }
        )
        history.save()
    return ErrorDict(ErrorCode.OK)
