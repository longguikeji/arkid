from common.extension import InMemExtension
from .serializers import WeChatWorkExternalIdpSerializer
from .provider import WeChatWorkExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class WeChatWorkExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="WeChatWork",
            description="企业微信授权登录",
            provider=WeChatWorkExternalIdpProvider,
            serializer=WeChatWorkExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="WeChatWork",
            description="企业微信授权登录",
            provider=WeChatWorkExternalIdpProvider,
            serializer=WeChatWorkExternalIdpSerializer,
        )


extension = WeChatWorkExternalIdpExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="企业微信授权登录",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="hanbin@jinji-inc.com",
)
