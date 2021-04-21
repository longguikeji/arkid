from common.extension import InMemExtension
from .serializers import ArkIDExternalIdpSerializer
from .provider import ArkIDExternalIdpProvider
from .constants import KEY


class ArkIDExternalIdpExtension(InMemExtension):
    def start(self, runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="ArkID",
            description="ArkID External idP",
            provider=ArkIDExternalIdpProvider,
            serializer=ArkIDExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = ArkIDExternalIdpExtension(
    tags='login',
    name="arkid",
    description="arkid as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="insfocus@gmail.com",
)
