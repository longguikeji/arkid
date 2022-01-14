from runtime import Runtime
from common.extension import InMemExtension
from .provider import MssqlDataSyncProvider, MssqlDataSyncClientProvider
from .serializers import MssqlDataSyncSerializer, MssqlDataSyncClientSerializer


class MssqlDataSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_data_sync_extension(
            key='mssql_data_sync_server',
            name='mssql_data_sync_server',
            description='Mssql Data Sync Extension',
            provider=MssqlDataSyncProvider,
            serializer=MssqlDataSyncSerializer,
        )
        runtime.register_data_sync_extension(
            key='mssql_data_sync_client',
            name='mssql_data_sync_client',
            description='Mssql Data Sync Client Extension',
            provider=MssqlDataSyncClientProvider,
            serializer=MssqlDataSyncClientSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_data_sync_extension(
            key='mssql_data_sync_server',
            name='mssql_data_sync_server',
            description='Mssql Data Sync Extension',
            provider=MssqlDataSyncProvider,
            serializer=MssqlDataSyncSerializer,
        )
        runtime.logout_data_sync_extension(
            key='mssql_data_sync_client',
            name='mssql_data_sync_client',
            description='Mssql Data Sync Client Extension',
            provider=MssqlDataSyncClientProvider,
            serializer=MssqlDataSyncClientSerializer,
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
    maintainer='fanhe@longguikeji.com',
)
