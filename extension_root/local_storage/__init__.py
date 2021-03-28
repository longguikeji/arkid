import typing
from runtime import Runtime
from extension.models import Extension
from .provider import LocalStorageProvider
from .constants import KEY


class LocalStorageExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        provider = LocalStorageProvider()
        provider.data_path = self.config('data_path')        

        runtime.register_storage_provider(
            provider=provider,
        )

        super().start(runtime=runtime, *args, **kwargs)


extension = LocalStorageExtension(
    name=KEY,
    description='local filesystem based storage solution',
    version='1.0',    
    logo='',
    maintainer='北京龙归科技有限公司',
    homepage='https://www.longguikeji.com',
    contact='rock@longguikeji.com',
)
