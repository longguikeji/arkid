from django.apps import AppConfig

class ExtensionConfig(AppConfig):

    name = 'arkid.extension'

    def ready(self):
        from arkid.common.check_arstore import check_extensions_expired
        check_extensions_expired()

        from .loader import ExtensionLoader
        ExtensionLoader()


