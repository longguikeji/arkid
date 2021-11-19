from runtime import Runtime
from common.extension import InMemExtension
from .provider import MssqlDataSyncProvider
from .serializers import MssqlDataSyncSerializer


class MssqlDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='mssql_data_sync',
            name='mssql_data_sync',
            description='Mssql Data Sync Extension',
            provider=MssqlDataSyncProvider,
            serializer=MssqlDataSyncSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='mssql_data_sync',
            name='mssql_data_sync',
            description='Mssql Data Sync Extension',
            provider=MssqlDataSyncProvider,
            serializer=MssqlDataSyncSerializer,
        )


extension = MssqlDataSyncExtension(
    name='mssql_data_sync',
    tags='mssql_data_sync',
    description='Mssql数据同步插件',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    scope='global',
    type='global',
    maintainer='rock@longguikeji.com',
)
