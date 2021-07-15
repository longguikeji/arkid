from common.extension import InMemExtension
from .constants import KEY
from .provider import FeishuExternalIdpProvider
from .serializers import FeishuExternalIdpSerializer
from runtime import Runtime


class FeishuExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='飞书',
            description='字节跳动出品的即时沟通工具',
            provider=FeishuExternalIdpProvider,
            serializer=FeishuExternalIdpSerializer,
        )
        super().start(runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name='飞书',
            description='字节跳动出品的即时沟通工具',
            provider=FeishuExternalIdpProvider,
            serializer=FeishuExternalIdpSerializer,
        )


extension = FeishuExtension(
    name='feishu',
    tags='login',
    scope='tenant',
    type='tenant',
    description='飞书',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
