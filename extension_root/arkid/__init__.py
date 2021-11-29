from common.extension import InMemExtension
from .serializers import ArkIDExternalIdpSerializer
from .provider import ArkIDExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class ArkIDExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="ArkID",
            description="ArkID External idP",
            provider=ArkIDExternalIdpProvider,
            serializer=ArkIDExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="ArkID",
            description="ArkID External idP",
            provider=ArkIDExternalIdpProvider,
            serializer=ArkIDExternalIdpSerializer,
        )



extension = ArkIDExternalIdpExtension(
    tags='login',
    name="arkid",
    scope='tenant',
    type='tenant',
    description="arkid as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="hanbin@jinji-inc.com",
)
