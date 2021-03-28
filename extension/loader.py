from .utils import load_installed_extensions
from common.logger import logger

class ExtensionLoader:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance._start()

        return cls._instance

    def _start(self):
        from runtime import get_app_runtime
        app_runtime = get_app_runtime()

        load_installed_extensions(
            runtime=app_runtime,
        )
        xx

        if app_runtime.sms_provider is None:
            logger.warning('SMS Provider not set')

        if app_runtime.cache_provider is None:
            logger.warning('Cache Provider not set')
