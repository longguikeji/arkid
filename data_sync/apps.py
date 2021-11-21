from django.apps import AppConfig


class SyncTasksConfig(AppConfig):
    name = 'data_sync'

    def ready(self):
        from . import signals
