from runtime import Runtime
from common.extension import InMemExtension
from .provider import MysqlStatisticsProvider


class MysqlStatisticsExtension(InMemExtension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        cache_provider = MysqlStatisticsProvider()
        runtime.register_statistics_provider(cache_provider)
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        cache_provider = MysqlStatisticsProvider()
        runtime.logout_statistics_provider(cache_provider)
