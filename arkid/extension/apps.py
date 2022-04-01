from django.apps import AppConfig

class ExtensionConfig(AppConfig):

    name = 'arkid.extension'

    def ready(self):
        from .loader import ExtensionLoader
        ExtensionLoader()


