from django.apps import AppConfig

class AppConfig(AppConfig):
    name = 'app'

    def ready(self) -> None:
        return super().ready()

