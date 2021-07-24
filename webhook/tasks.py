import logging
import json
from enum import Enum
from json import JSONDecodeError
from typing import TYPE_CHECKING
from urllib.parse import urlparse, urlunparse

import requests
from celery.utils.log import get_task_logger
from requests.exceptions import RequestException
from celery import shared_task
from .event_types import WebhookEventType
from .models import Webhook, WebhookTriggerHistory
from . import signature_for_payload

logger = logging.getLogger(__name__)
task_logger = get_task_logger(__name__)

WEBHOOK_TIMEOUT = 10


class WebhookSchemes(str, Enum):
    HTTP = "http"
    HTTPS = "https"


def _get_webhooks_for_event(event_type, webhooks=None):
    """Get active webhooks from the database for an event."""

    if webhooks is None:
        webhooks = Webhook.objects.all()

    webhooks = webhooks.filter(
        is_active=True,
        events__event_type__in=[event_type, WebhookEventType.ANY],
    ).distinct()
    
    return webhooks


@shared_task(compression='zlib')
def trigger_webhooks_for_event(event_type, data):
    """Send a webhook request for an event as an async task."""
    webhooks = _get_webhooks_for_event(event_type)
    for webhook in webhooks:
        send_webhook_request.delay(
            webhook.uuid.hex, webhook.url, webhook.secret, event_type, data
        )


def send_webhook_using_http(webhook_uuid, target_url, message, signature, event_type):
    headers = {
        "Content-Type": "application/json",
        "X-Arkid-Event": event_type,
        "X-Arkid-Signature": signature,
    }

    hook = Webhook.valid_objects.get(uuid=webhook_uuid)
    request_data = json.dumps({'headers': headers, 'body': message.decode('utf-8')})
    history = WebhookTriggerHistory.objects.create(
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


@shared_task(
    autoretry_for=(RequestException,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
    compression="zlib",
)
def send_webhook_request(webhook_uuid, target_url, secret, event_type, data):
    parts = urlparse(target_url)
    message = data.encode("utf-8")
    signature = signature_for_payload(message, secret)
    if parts.scheme.lower() in [WebhookSchemes.HTTP, WebhookSchemes.HTTPS]:
        send_webhook_using_http(
            webhook_uuid, target_url, message, signature, event_type
        )
    else:
        raise ValueError("Unknown webhook scheme: %r" % (parts.scheme,))

    task_logger.debug(
        "[Webhook ID:%r] Payload sent to %r for event %r",
        webhook_uuid,
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
