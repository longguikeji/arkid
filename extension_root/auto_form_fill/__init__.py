from runtime import Runtime
from common.extension import InMemExtension
from .provider import AutoFormFillAppTypeProvider


class AutoFormFillExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        from .serializers.AutoFormFillAppSerializer import AutoFormFillAppSerializer
        runtime.register_app_type(
            key='auto_form_fill',
            name='automatic form fill',
            provider=AutoFormFillAppTypeProvider,
            serializer=AutoFormFillAppSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        from .serializers.AutoFormFillAppSerializer import AutoFormFillAppSerializer
        runtime.logout_app_type(
            key='auto_form_fill',
            name='automatic form fill',
            provider=AutoFormFillAppTypeProvider,
            serializer=AutoFormFillAppSerializer,
        )


extension = AutoFormFillExtension(
    scope='tenant',
    type='tenant',
    tags='AutoFormFill',
    name='auto_form_fill',
    description='Auto From Fill',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='support@longguikeji.com',
)
