import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')
django.setup()

from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.event import Event, dispatch_event, APP_START
from arkid.core.perm.permission_data import PermissionData
from arkid.config import get_app_config
from arkid.common.logger import logger
from arkid.core.models import Tenant
from types import SimpleNamespace
from arkid.core.api import api
from celery import shared_task
from .celery import app
import requests, uuid
import importlib

from urllib.parse import urlparse, urlunparse
import requests
from enum import Enum
from webhook.models import Webhook, WebhookTriggerHistory
from webhook import signature_for_payload
from celery.utils.log import get_task_logger
import json
from requests.exceptions import RequestException
from json import JSONDecodeError

task_logger = get_task_logger(__name__)
WEBHOOK_TIMEOUT = 5


@app.task(bind=True)
def sync(self, config_id, *args, **kwargs):

    try:
        logger.info("=== arkid.core.tasks.sync start...===")
        logger.info(f"config_id: {config_id}")
        logger.info(f"kwargs: {kwargs}")
        extension_config = TenantExtensionConfig.active_objects.get(id=config_id)
        extension = extension_config.extension
        ext_dir = extension.ext_dir
        logger.info(f"Importing  {ext_dir}")
        ext_name = str(ext_dir).replace('/', '.')
        ext = importlib.import_module(ext_name)
        if ext and hasattr(ext, 'extension'):
            ext.extension.sync(extension_config)
            logger.info("=== arkid.core.tasks.sync end...===")
        else:
            logger.error(f'{ext_name} import fail')
            return None
    except Exception as exc:
        max_retries = kwargs.get('max_retries', 3)
        countdown = kwargs.get('retry_delay', 5 * 60)
        raise self.retry(exc=exc, max_retries=max_retries, countdown=countdown)


@app.task
def update_app_permission(tenant_id, app_id):
    '''
    更新应用权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_app_permission(tenant_id, app_id)


@app.task
def update_system_permission():
    '''
    更新系统权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_system_permission()


@app.task
def update_single_user_system_permission(tenant_id, user_id):
    '''
    更新单个用户的系统权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_single_user_system_permission(tenant_id, user_id)


@app.task
def update_single_user_app_permission(tenant_id, user_id, app_id):
    '''
    更新单个用户的应用权限
    '''
    permissiondata = PermissionData()
    permissiondata.update_single_user_app_permission(tenant_id, user_id, app_id)


@app.task
def add_system_permission_to_user(self, tenant_id, user_id, permission_id):
    '''
    添加系统权限给用户
    '''
    permissiondata = PermissionData()
    permissiondata.add_system_permission_to_user(tenant_id, user_id, permission_id)


class WebhookSchemes(str, Enum):
    HTTP = "http"
    HTTPS = "https"


def _get_webhooks_for_event(tenant_id, event_type):
    """Get active webhooks from the database for an event."""

    tenant = Tenant.valid_objects.get(id=tenant_id)
    webhooks = Webhook.valid_objects.filter(
        tenant=tenant,
        events__event_type__in=[event_type],
    ).distinct()
    return webhooks


@app.task(compression='zlib')
def trigger_webhooks_for_event(tenant_id, event_type, data):
    """Send a webhook request for an event as an async task."""
    webhooks = _get_webhooks_for_event(tenant_id, event_type)
    logger.info(webhooks)
    for webhook in webhooks:
        send_webhook_request.delay(
            webhook.id.hex, webhook.url, webhook.secret, event_type, data
        )


def send_webhook_using_http(webhook_id, target_url, message, signature, event_type):
    headers = {
        "Content-Type": "application/json",
        "X-Arkid-Event": event_type,
        "X-Arkid-Signature": signature,
    }

    hook = Webhook.valid_objects.get(id=webhook_id)
    request_data = json.dumps({'headers': headers, 'body': message.decode('utf-8')})
    history = WebhookTriggerHistory.objects.create(
        tenant=hook.tenant,
        webhook=hook,
        status='waiting',
        request=request_data,
        response=None,
    )
    response = None
    try:
        response = requests.post(
            target_url, data=message, headers=headers, timeout=WEBHOOK_TIMEOUT
        )
        response.raise_for_status()
    except Exception as exc:
        if response:
            status_code = response.status_code
        else:
            status_code = None
        response_data = json.dumps({'status_code': status_code, 'body': str(exc)})
        history.status = 'failed'
        history.response = response_data
        history.save()
        raise exc
    else:
        status_code = response.status_code
        response_data = json.dumps({'status_code': status_code, 'body': response.text})
        history.status = 'success'
        history.response = response_data
        history.save()
    return response


@app.task(
    autoretry_for=(RequestException,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 2},
    compression="zlib",
)
def send_webhook_request(webhook_id, target_url, secret, event_type, data):
    parts = urlparse(target_url)
    message = data.encode("utf-8")
    signature = signature_for_payload(message, secret)
    if parts.scheme.lower() in [WebhookSchemes.HTTP, WebhookSchemes.HTTPS]:
        send_webhook_using_http(webhook_id, target_url, message, signature, event_type)
    else:
        raise ValueError("Unknown webhook scheme: %r" % (parts.scheme,))

    task_logger.debug(
        "[Webhook ID:%r] Payload sent to %r for event %r",
        webhook_id,
        target_url,
        event_type,
    )


def send_webhook_request_sync(webhook_uuid, target_url, secret, event_type, data: str):
    parts = urlparse(target_url)
    message = data.encode("utf-8")
    signature = signature_for_payload(message, secret)

    response_data = None
    if parts.scheme.lower() in [WebhookSchemes.HTTP, WebhookSchemes.HTTPS]:
        logger.debug(
            "[Webhook] Sending payload to %r for event %r.", target_url, event_type
        )
        try:
            response = send_webhook_using_http(
                webhook_uuid, target_url, message, signature, event_type
            )
            response_data = response.json()
        except RequestException as e:
            logger.debug("[Webhook] Failed request to %r: %r.", target_url, e)
        except JSONDecodeError as e:
            logger.debug(
                "[Webhook] Failed parsing JSON response from %r: %r.", target_url, e
            )
        else:
            logger.debug("[Webhook] Success response from %r.", target_url)
    else:
        raise ValueError("Unknown webhook scheme: %r" % (parts.scheme,))
    return response_data
