from email.policy import default
from arkid.extension.utils import load_active_extensions, find_available_extensions
from common.logger import logger
from arkid.extension.models import Extension


class ExtensionLoader:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._instance._start()

        return cls._instance

    def _start(self):
        exts = find_available_extensions()
        for ext in exts:
            Extension.objects.update_or_create(
                defaults={
                    'labels': ext.labels,
                    'name': ext.name,
                    'is_active': True,
                },
                package = ext.package,
                version = ext.version
            )
        load_active_extensions()
