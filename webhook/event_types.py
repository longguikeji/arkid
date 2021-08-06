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

    DISPLAY_LABELS = {
        ANY: "Any events",
        USER_CREATED: 'User created',
        USER_UPDATED: 'User updated',
        USER_DELETED: 'User deleted',
        GROUP_CREATED: 'Group created',
        GROUP_UPDATED: 'Group updated',
        GROUP_DELETED: 'Group deleted',
        APP_CREATED: 'App created',
        APP_UPDATED: 'App updated',
        APP_DELETED: 'App deleted',
    }

    CHOICES = [
        (ANY, DISPLAY_LABELS[ANY]),
        (USER_CREATED, DISPLAY_LABELS[USER_DELETED]),
        (USER_UPDATED, DISPLAY_LABELS[USER_UPDATED]),
        (USER_DELETED, DISPLAY_LABELS[USER_UPDATED]),
        (GROUP_CREATED, DISPLAY_LABELS[GROUP_CREATED]),
        (GROUP_UPDATED, DISPLAY_LABELS[GROUP_UPDATED]),
        (GROUP_DELETED, DISPLAY_LABELS[GROUP_DELETED]),
        (APP_CREATED, DISPLAY_LABELS[APP_CREATED]),
        (APP_UPDATED, DISPLAY_LABELS[APP_UPDATED]),
        (APP_DELETED, DISPLAY_LABELS[APP_DELETED]),
    ]
