from runtime import Runtime
from common.extension import InMemExtension
from .provider import AdDataSyncProvider, AdDataSyncClientProvider
from .serializers import AdDataSyncSerializer, AdDataSyncClientSerializer


class AdDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='ad_data_sync_server',
            name='ad_data_sync_server',
            description='AD Data Sync Extension',
            provider=AdDataSyncProvider,
            serializer=AdDataSyncSerializer,
        )
        runtime.register_data_sync_extension(
            key='ad_data_sync_client',
            name='ad_data_sync_client',
            description='AD Data Sync Client Extension',
            provider=AdDataSyncClientProvider,
            serializer=AdDataSyncClientSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='ad_data_sync_client',
            name='ad_data_sync_client',
            description='AD Data Sync Extension',
            provider=AdDataSyncProvider,
            serializer=AdDataSyncSerializer,
        )
        runtime.logout_data_sync_extension(
            key='arkid_data_sync_client',
            name='arkid_data_sync_client',
            description='AD Data Sync Client Extension',
            provider=AdDataSyncClientProvider,
            serializer=AdDataSyncClientSerializer,
        )


extension = AdDataSyncExtension(
    name='ad_data_sync',
    tags='ad_data_sync',
    description='AD数据同步插件',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    scope='global',
    type='global',
    maintainer='fanhe@longguikeji.com',
)
