from typing import Optional, Callable

from config import Config, get_app_config
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class InMemExtension:

    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    homepage: Optional[str] = None
    logo: Optional[str] = None
    maintainer: Optional[str] = None
    tags: Optional[str] = None
    type: Optional[str] = None

    scope: Optional[str] = None

    on_start: Optional[Callable] = None
    serializer: ExtensionBaseSerializer = None

    def __init__(self, *args, **kwargs) -> None:
        if self.scope is None:
            self.scope = kwargs.get('scope', None)

        if self.name is None:
            self.name = kwargs.get('name', None)

        if self.version is None:
            self.version = kwargs.get('version', None)

        if self.description is None:
            self.description = kwargs.get('description', None)

        if self.homepage is None:
            self.homepage = kwargs.get('homepage', None)

        if self.logo is None:
            self.logo = kwargs.get('logo', None)

        if self.maintainer is None:
            self.maintainer = kwargs.get('maintainer', None)

        if self.on_start is None:
            self.on_start = kwargs.get('on_start', None)

        if self.tags is None:
            self.tags = kwargs.get('tags', None)

        if self.type is None:
            self.type = kwargs.get('type', None)

        serializer = kwargs.get('serializer', None)
        if serializer is not None:
            self.serializer = serializer
        else:
            self.serializer = ExtensionBaseSerializer

    def __str__(self) -> str:
        return f'Extension: {self.name}'

    def __repr__(self) -> str:
        return f'Extension: {self.name}'

    def start(self, runtime) -> None:
        if self.on_start is not None:
            self.on_start(runtime)

    def config(self, key, default=None) -> any:
        app_config: Config = get_app_config()
        value = app_config.extension.config.get(self.name, None)
        if value is None:
            return None

        value = value.get(key, default)
        return value

    def register(self, service_name):
        pass
