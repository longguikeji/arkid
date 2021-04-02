from django.apps import AppConfig

class ExtensionConfig(AppConfig):

    name = 'extension'

    def ready(self):
        from .loader import ExtensionLoader
        # ExtensionLoader()

