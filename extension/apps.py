from django.apps import AppConfig
from .loader import ExtensionLoader


class ExtensionConfig(AppConfig):

    name = 'extension'

    def ready(self):
        ExtensionLoader()    

