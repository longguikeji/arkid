from runtime import Runtime
from extension.models import Extension
from .provider import RedisCacheProvider


class RedisCacheExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        cache_provider = RedisCacheProvider(
            host=self.config('host'),
            port=self.config('port'),
            db=self.config('db'),
            password=self.config('password'),
        )

        runtime.cache_provider = cache_provider
        print('>>>', runtime.cache_provider)

        super().start(runtime=runtime, *args, **kwargs)