from common.extension import InMemExtension

from .provider import AuthCodeProvider
from runtime import Runtime
from .constants import KEY


class AuthCodeExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_other_auth_factor(
            key=KEY,
            name="mobile_login_register",
            description="Mobile login and register",
            provider=AuthCodeProvider,
            serializer=None,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_other_auth_factor(
            key=KEY,
            name="mobile_login_register",
            description="Mobile login register config",
            provider=AuthCodeProvider,
            serializer=None,
        )


extension = AuthCodeExtension(
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
