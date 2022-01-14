from common.extension import InMemExtension
from .serializers import WeChatScanExternalIdpSerializer
from .provider import WeChatScanExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class WeChatScanExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="WeChatScan",
            description="WeChatScan External idP",
            provider=WeChatScanExternalIdpProvider,
            serializer=WeChatScanExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="WeChatScan",
            description="WeChatScan External idP",
            provider=WeChatScanExternalIdpProvider,
            serializer=WeChatScanExternalIdpSerializer,
        )


extension = WeChatScanExternalIdpExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="wechatscan as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="hanbin@jinji-inc.com",
)
