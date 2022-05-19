from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from webhook.models import Webhook, WebhookEvent, WebhookTriggerHistory
from arkid.core.error import ErrorCode
from typing import List
from ninja.pagination import paginate
from ninja import ModelSchema, Schema
from pydantic import Field
import json
import requests


class WebhookSchemaOut(ModelSchema):
    class Config:
        model = Webhook
        model_fields = ['id', 'name', 'url', 'secret']

    events: List[str]

    @staticmethod
    def resolve_events(obj):
        events = []
        for e in obj.events_set.all():
            events.append(e.event_type)
        return events


class WebhookSchemaIn(Schema):
    name: str = Field(title=_('Name', '名称'), default='')
    url: str = Field(title=_('URL', '应用URL'))
    secret: str = Field(title=_('Secret', '签名密钥'), defaut='')
    events: List[str] = Field(title=_('Events', '监听事件'))


@api.get(
    "/tenant/{tenant_id}/webhooks/",
    tags=["Webhook"],
    auth=None,
    response=List[WebhookSchemaOut],
)
@paginate
def get_webhooks(request, tenant_id: str):
    tenant = request.tenant
    webhooks = Webhook.valid_objects.filter(tenant=tenant)
    return webhooks


@api.get(
    "/tenant/{tenant_id}/webhooks/{id}/",
    tags=["Webhook"],
    auth=None,
    response=WebhookSchemaOut,
)
def get_webhook(request, tenant_id: str, id: str):
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    else:
        return webhook


@api.post(
    "/tenant/{tenant_id}/webhooks/",
    tags=["Webhook"],
    auth=None,
    response=WebhookSchemaOut,
)
def create_webhook(request, tenant_id: str, data: WebhookSchemaIn):
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
    auth=None,
    response=WebhookSchemaOut,
)
def update_webhook(request, tenant_id: str, id: str, data: WebhookSchemaIn):
    tenant = request.tenant
    name = data.name
    url = data.url
    secret = data.secret
    events = data.events
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    webhook.events_set.clear()
    webhook.name = name
    webhook.url = url
    webhook.secret = secret
    for event in events:
        webhook_event, _ = WebhookEvent.valid_objects.update_or_create(event_type=event)
        webhook.events_set.add(webhook_event)
    webhook.save()
    return webhook


@api.delete("/tenant/{tenant_id}/webhooks/{id}/", tags=["Webhook"], auth=None)
def delete_webhook(request, tenant_id: str, id: str):
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    else:
        webhook.delete()
        return {'error': ErrorCode.OK.value}


class WebhookHistorySchemaOut(ModelSchema):
    class Config:
        model = WebhookTriggerHistory
        model_fields = ['id', 'status', 'request', 'response']


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/",
    tags=["Webhook"],
    auth=None,
    response=List[WebhookHistorySchemaOut],
)
@paginate
def get_webhook_histories(request, tenant_id: str, webhook_id: str):
    """获取Webhook历史记录列表"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    histories = webhook.history_set.all()
    return histories


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/",
    tags=["Webhook"],
    auth=None,
    response=WebhookHistorySchemaOut,
)
def get_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """获取Webhook历史记录,TODO"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    history = WebhookTriggerHistory.valid_objects.filter(webhook=webhook, id=id).first()
    if not history:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    return history


@api.get(
    "/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/retry/",
    tags=["Webhook"],
    auth=None,
)
def retry_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """重试webhook历史记录,TODO"""
    tenant = request.tenant
    webhook = Webhook.valid_objects.filter(tenant=tenant, id=webhook_id).first()
    if not webhook:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}
    history = WebhookTriggerHistory.valid_objects.filter(webhook=webhook, id=id).first()
    if not history:
        return {'error': ErrorCode.WEBHOOK_NOT_EXISTS.value}

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
    return {'error': ErrorCode.OK.value}
