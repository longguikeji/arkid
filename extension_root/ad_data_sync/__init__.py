from runtime import Runtime
from common.extension import InMemExtension
from .provider import AdDataSyncProvider
from .serializers import AdDataSyncSerializer


class AdDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='ad_data_sync',
            name='ad_data_sync',
            description='AD Data Sync Extension',
            provider=AdDataSyncProvider,
            serializer=AdDataSyncSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='ad_data_sync',
            name='ad_data_sync',
            description='AD Data Sync Extension',
            provider=AdDataSyncProvider,
            serializer=AdDataSyncSerializer,
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
    maintainer='rock@longguikeji.com',
)
