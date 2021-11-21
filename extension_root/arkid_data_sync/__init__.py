from runtime import Runtime
from common.extension import InMemExtension
from .provider import ArkidDataSyncProvider, ArkidDataSyncClientProvider
from .serializers import ArkidDataSyncSerializer, ArkIDDataSyncClientSerializer
from .tasks import sync


class ArkidDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='arkid_data_sync_server',
            name='arkid_data_sync_server',
            description='Arkid Data Sync Server Extension',
            provider=ArkidDataSyncProvider,
            serializer=ArkidDataSyncSerializer,
        )
        runtime.register_data_sync_extension(
            key='arkid_data_sync_client',
            name='arkid_data_sync_client',
            description='Arkid Data Sync Client Extension',
            provider=ArkidDataSyncClientProvider,
            serializer=ArkIDDataSyncClientSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='arkid_data_sync_server',
            name='arkid_data_sync_server',
            description='Arkid Data Sync Server Extension',
            provider=ArkidDataSyncProvider,
            serializer=ArkidDataSyncSerializer,
        )
        runtime.logout_data_sync_extension(
            key='arkid_data_sync_client',
            name='arkid_data_sync_client',
            description='Arkid Data Sync Client Extension',
            provider=ArkidDataSyncClientProvider,
            serializer=ArkIDDataSyncClientSerializer,
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
