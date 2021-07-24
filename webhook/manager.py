from .event_types import WebhookEventType
from .tasks import trigger_webhooks_for_event
from .payloads import (
    # generate_app_payload,
    generate_user_payload,
    generate_group_payload,
    generate_dept_payload,
)


class WebhookManager:
    # @classmethod
    # def app_created(cls, tenant_uuid, app):
    #     app_data = generate_app_payload(app)
    #     trigger_webhooks_for_event.delay(
    #         tenant_uuid, WebhookEventType.APP_CREATED, app_data
    #     )

    # @classmethod
    # def app_updated(cls, tenant_uuid, app):
    #     app_data = generate_app_payload(app)
    #     trigger_webhooks_for_event.delay(
    #         tenant_uuid, WebhookEventType.APP_UPDATED, app_data
    #     )

    # @classmethod
    # def app_deleted(cls, tenant_uuid, app):
    #     app_data = generate_app_payload(app)
    #     trigger_webhooks_for_event.delay(
    #         tenant_uuid, WebhookEventType.APP_DELETED, app_data
    #     )

    @classmethod
    def user_created(cls, user):
        user_data = generate_user_payload(user)
        trigger_webhooks_for_event.delay(WebhookEventType.USER_CREATED, user_data)

    @classmethod
    def user_registered(cls, user):
        user_data = generate_user_payload(user, from_register=True)
        trigger_webhooks_for_event.delay(WebhookEventType.USER_REGISTERED, user_data)

    @classmethod
    def user_updated(cls, user):
        user_data = generate_user_payload(user)
        trigger_webhooks_for_event.delay(WebhookEventType.USER_UPDATED, user_data)

    @classmethod
    def user_deleted(cls, user):
        user_data = generate_user_payload(user)
        trigger_webhooks_for_event.delay(WebhookEventType.USER_DELETED, user_data)

    @classmethod
    def group_created(cls, group):
        group_data = generate_group_payload(group)
        trigger_webhooks_for_event.delay(WebhookEventType.GROUP_CREATED, group_data)

    @classmethod
    def group_updated(cls, group):
        group_data = generate_group_payload(group)
        trigger_webhooks_for_event.delay(WebhookEventType.GROUP_UPDATED, group_data)

    @classmethod
    def group_deleted(cls, group):
        group_data = generate_group_payload(group)
        trigger_webhooks_for_event.delay(WebhookEventType.GROUP_DELETED, group_data)

    @classmethod
    def dept_created(cls, dept):
        dept_data = generate_dept_payload(dept)
        trigger_webhooks_for_event.delay(WebhookEventType.DEPT_CREATED, dept_data)

    @classmethod
    def dept_updated(cls, dept):
        dept_data = generate_dept_payload(dept)
        trigger_webhooks_for_event.delay(WebhookEventType.DEPT_UPDATED, dept_data)

    @classmethod
    def dept_deleted(cls, dept):
        dept_data = generate_dept_payload(dept)
        trigger_webhooks_for_event.delay(WebhookEventType.DEPT_DELETED, dept_data)
