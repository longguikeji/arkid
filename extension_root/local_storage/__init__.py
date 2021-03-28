from runtime import Runtime
from common.extension import InMemExtension
from .provider import LocalStorageProvider
from .constants import KEY
from .serializers import LocalStorageSerializer

class LocalStorageExtension(InMemExtension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        provider = LocalStorageProvider()

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
    serializer=LocalStorageSerializer,
)
