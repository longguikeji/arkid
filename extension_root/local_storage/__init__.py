import typing
from runtime import Runtime
from extension.models import Extension
from django.urls import path, include


class DemoExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        print('loaded config > ', self.config('config1'))
        super().start(runtime=runtime, *args, **kwargs)


extension = DemoExtension(
    name='demo',
    description='demonstration only',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
