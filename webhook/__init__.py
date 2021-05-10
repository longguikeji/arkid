from .events import ModelEvent
from inventory.models import User, Group
from app.models import App
from django.db.models.signals import post_save, post_delete

user_created_event = ModelEvent('event.user.created', User, post_save)
user_updated_event = ModelEvent('event.user.updated', User, post_save)
user_deleted_event = ModelEvent('event.user.deleted', User, post_delete)

group_created_event = ModelEvent('event.group.created', Group, post_save)
group_updated_event = ModelEvent('event.group.updated', Group, post_save)
group_deleted_event = ModelEvent('event.group.deleted', Group, post_delete)

app_created_event = ModelEvent('event.app.created', App, post_save)
app_updated_event = ModelEvent('event.app.updated', App, post_save)
app_deleted_event = ModelEvent('event.app.deleted', App, post_delete)
