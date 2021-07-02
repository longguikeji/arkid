from enum import Enum
from django.db import models
from django.utils.translation import gettext_lazy as _


class Event(models.TextChoices):

    USER_CREATED = ('event.user.created', _('USER_CREATED'))
    USER_UPDATED = 'event.user.updated', _('USER_UPDATED')
    USER_DELETED = 'event.user.deleted', _('USER_DELETED')

    GROUP_CREATED = 'event.group.created', _('GROUP_CREATED')
    GROUP_UPDATED = 'event.group.updated', _('GROUP_UPDATED')
    GROUP_DELETED = 'event.group.deleted', _('GROUP_DELETED')

    APP_CREATED = 'event.app.created', _('APP_CREATED')
    APP_UPDATED = 'event.app.updated', _('APP_UPDATED')
    APP_DELETED = 'event.app.deleted', _('APP_DELETED')
