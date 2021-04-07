from common.extension import InMemExtension
from .constants import KEY
from .provider import FeishuExternalIdpProvider
from .serializers import FeishuExternalIdpSerializer


class FeishuExtension(InMemExtension):

    def start(self, runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='飞书',
            description='字节跳动出品的即时沟通工具',
            provider=FeishuExternalIdpProvider,
            serializer=FeishuExternalIdpSerializer,
        )
        super().start(runtime, *args, **kwargs)


extension = FeishuExtension(
    scope='tenant',  # TODO: to support tenant isolated extension
    name='feishu',
    description='飞书',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
