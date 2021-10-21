from .event_types import WebhookEventType
from .tasks import trigger_webhooks_for_event
from .payloads import (
    generate_app_payload,
    generate_user_payload,
    generate_group_payload,
)
from celery.utils.log import get_logger

logger = get_logger(__name__)


class WebhookManager:
    @classmethod
    def app_created(cls, tenant_uuid, app):
        app_data = generate_app_payload(app)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.APP_CREATED, app_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def app_updated(cls, tenant_uuid, app):
        app_data = generate_app_payload(app)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.APP_UPDATED, app_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def app_deleted(cls, tenant_uuid, app):
        app_data = generate_app_payload(app)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.APP_DELETED, app_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def user_created(cls, tenant_uuid, user):
        user_data = generate_user_payload(user)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.USER_CREATED, user_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def user_updated(cls, tenant_uuid, user):
        user_data = generate_user_payload(user)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.USER_UPDATED, user_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def user_deleted(cls, tenant_uuid, user):
        user_data = generate_user_payload(user)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.USER_DELETED, user_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def group_created(cls, tenant_uuid, group):
        group_data = generate_group_payload(group)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.GROUP_CREATED, group_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def group_updated(cls, tenant_uuid, group):
        group_data = generate_group_payload(group)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.GROUP_UPDATED, group_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)

    @classmethod
    def group_deleted(cls, tenant_uuid, group):
        group_data = generate_group_payload(group)
        try:
            trigger_webhooks_for_event.delay(
                tenant_uuid, WebhookEventType.GROUP_DELETED, group_data
            )
        except Exception as exc:
            logger.exception('Sending task raised: %r', exc)
