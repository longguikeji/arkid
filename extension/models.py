import typing

from config import Config, get_app_config
from django.db import models

class Extension:

    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    version: typing.Optional[str] = None
    homepage: typing.Optional[str] = None
    logo: typing.Optional[str] = None
    maintainer: typing.Optional[str] = None

    scope: str = 'global'
    
    on_start: typing.Optional[typing.Callable] = None

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

    def __str__(self) -> str:
        return f'Extension: {self.name}'

    def __repr__(self) -> str:
        return f'Extension: {self.name}'

    def start(self, runtime) -> None:
        if self.on_start is not None:
            self.on_start(runtime)

    def config(self, key) -> any:
        app_config: Config = get_app_config()
        value = app_config.extension.config.get(self.name, None)
        if value is None:
            return None
        
        value = value.get(key, None)
        return value

    def register(self, service_name):
        pass

    