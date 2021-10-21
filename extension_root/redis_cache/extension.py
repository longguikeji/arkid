from runtime import Runtime
from common.extension import InMemExtension
from .provider import RedisCacheProvider


class RedisCacheExtension(InMemExtension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        cache_provider = RedisCacheProvider(
            host=self.config('host'),
            port=self.config('port'),
            db=self.config('db'),
            password=self.config('password'),
        )

        runtime.register_cache_provider(cache_provider)
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        cache_provider = RedisCacheProvider(
            host=self.config('host'),
            port=self.config('port'),
            db=self.config('db'),
            password=self.config('password'),
        )
        runtime.logout_cache_provider(cache_provider)