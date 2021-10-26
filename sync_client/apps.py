from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'sync_client'

    def ready(self):
        from sync_client.tasks import create_task
        create_task()
