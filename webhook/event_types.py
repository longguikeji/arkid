#!/usr/bin/env python3


class WebhookEventType:
    ANY = "any_events"

    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'

    GROUP_CREATED = 'group_created'
    GROUP_UPDATED = 'group_updated'
    GROUP_DELETED = 'group_deleted'

    APP_CREATED = 'app_created'
    APP_UPDATED = 'app_updated'
    APP_DELETED = 'app_deleted'
