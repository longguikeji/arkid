from runtime import Runtime
from common.extension import InMemExtension
from django.urls import path, include


class DemoExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        print('loaded config > ', self.config('config1'))
        super().start(runtime=runtime, *args, **kwargs)


extension = DemoExtension(
    name='demo',
    description='demonstration only',
    version='1.0',
    scope='tenant',
    type='tenant',
    homepage='https://www.longguikeji.com',
    logo='',
    tags='demo',
    maintainer='hanbin@jinji-inc.com',
)
