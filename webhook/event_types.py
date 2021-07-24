#!/usr/bin/env python3


class WebhookEventType:
    ANY = "any_events"

    USER_CREATED = 'user_created'
    USER_REGISTERED = 'user_registered'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'

    GROUP_CREATED = 'group_created'
    GROUP_UPDATED = 'group_updated'
    GROUP_DELETED = 'group_deleted'

    DEPT_CREATED = 'dept_created'
    DEPT_UPDATED = 'dept_updated'
    DEPT_DELETED = 'dept_deleted'

    # APP_CREATED = 'app_created'
    # APP_UPDATED = 'app_updated'
    # APP_DELETED = 'app_deleted'
