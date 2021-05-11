from django.apps import AppConfig


class WebhookConfig(AppConfig):
    name = 'webhook'

    def ready(self):
        # importing model classes
        from .events import (
            user_created_event,
            user_updated_event,
            user_deleted_event,
            group_created_event,
            group_updated_event,
            group_deleted_event,
            app_created_event,
            app_updated_event,
            app_deleted_event,
        )
