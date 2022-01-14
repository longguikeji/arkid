from runtime import Runtime
from common.extension import InMemExtension
from .provider import LocalStorageProvider
from .constants import KEY
from .serializers import LocalStorageSerializer


class LocalStorageExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None

        provider = LocalStorageProvider()
        provider.data_path = o.data.get('data_path')

        runtime.register_storage_provider(
            provider=provider,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = LocalStorageProvider()
        runtime.logout_storage_provider(
            provider=provider,
        )


extension = LocalStorageExtension(
    name=KEY,
    tags='storage',
    scope='global',
    type='global',
    description='local filesystem based storage solution',
    version='1.0',
    logo='',
    maintainer='hanbin@jinji-inc.com',
    homepage='https://www.longguikeji.com',
    contact='rock@longguikeji.com',
    serializer=LocalStorageSerializer,
)
