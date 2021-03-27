from runtime import Runtime
from extension.models import Extension
from .provider import InMemCacheProvider


class InMemCacheExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        cache_provider = InMemCacheProvider()

        runtime.cache_provider = cache_provider
        print('>>>', runtime.cache_provider)

        super().start(runtime=runtime, *args, **kwargs)