from common.extension import InMemExtension
from .serializers import WeChatWorkScanExternalIdpSerializer
from .provider import WeChatWorkScanExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class WeChatWorkScanExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="WeChatWorkScan",
            description="企业微信扫码登录",
            provider=WeChatWorkScanExternalIdpProvider,
            serializer=WeChatWorkScanExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="WeChatWorkScan",
            description="企业微信扫码登录",
            provider=WeChatWorkScanExternalIdpProvider,
            serializer=WeChatWorkScanExternalIdpSerializer,
        )


extension = WeChatWorkScanExternalIdpExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="企业微信扫码登录",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="hanbin@jinji-inc.com",
)
