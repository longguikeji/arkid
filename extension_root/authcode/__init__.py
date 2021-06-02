from common.extension import InMemExtension

from .provider import AuthCodeIdpProvider
from .constants import KEY
from .serializers import AuthCodeInfoSerializer


class AuthCodeExternalIdpExtension(InMemExtension):

    def start(self, runtime, *args, **kwargs):
        provider = AuthCodeIdpProvider()
        runtime.register_authcode_provider(
            authcode_provider=provider,
        )

        super().start(runtime=runtime, *args, **kwargs)


extension = AuthCodeExternalIdpExtension(
    name=KEY,
    tags='authcode',
    scope='global',
    type='global',
    description='系统自带图片验证码',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
    serializer=AuthCodeInfoSerializer,
)
