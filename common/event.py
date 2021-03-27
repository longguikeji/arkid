from enum import Enum


class Event(Enum):

    USER_CREATED = 'event.user.created'
    USER_UPDATED = 'event.user.updated'
    USER_DELETED = 'event.user.deleted'

    GROUP_CREATED = 'event.group.created'
    GROUP_UPDATED = 'event.group.updated'
    GROUP_DELETED = 'event.group.deleted'

    APP_CREATED = 'event.app.created'
    APP_UPDATED = 'event.app.updated'
    APP_DELETED = 'event.app.deleted'