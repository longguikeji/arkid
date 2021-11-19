from runtime import Runtime
from common.extension import InMemExtension
from .provider import ArkidDataSyncProvider
from .serializers import ArkidDataSyncSerializer


class ArkidDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='arkid_data_sync',
            name='arkid_data_sync',
            description='Arkid Data Sync Extension',
            provider=ArkidDataSyncProvider,
            serializer=ArkidDataSyncSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='arkid_data_sync',
            name='arkid_data_sync',
            description='Arkid Data Sync Extension',
            provider=ArkidDataSyncProvider,
            serializer=ArkidDataSyncSerializer,
        )


extension = ArkidDataSyncExtension(
    name='arkid_data_sync',
    tags='arkid_data_sync',
    description='Arkid数据同步插件',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    scope='global',
    type='global',
    maintainer='rock@longguikeji.com',
)
