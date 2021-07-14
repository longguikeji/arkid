from common.extension import InMemExtension

from .provider import AuthCodeIdpProvider
from runtime import Runtime
from .constants import KEY


class AuthCodeExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None

        provider = AuthCodeIdpProvider()
        runtime.register_authcode_provider(
            authcode_provider=provider,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = AuthCodeIdpProvider()
        runtime.logout_authcode_provider(
            authcode_provider=provider,
        )


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
)
