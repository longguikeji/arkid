from common.extension import InMemExtension
from .serializers import MobileLoginRegisterConfigSerializer
from .provider import MobileLoginRegisterConfigProvider
from runtime import Runtime
from .constants import KEY


class MobileLoginRegisterConfigExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_login_register_config(
            key=KEY,
            name="mobile-login-register",
            description="Mobile login and register",
            provider=MobileLoginRegisterConfigProvider,
            serializer=MobileLoginRegisterConfigSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_login_register_config(
            key=KEY,
            name="mobile-login-register",
            description="Mobile login register config",
            provider=MobileLoginRegisterConfigProvider,
            serializer=MobileLoginRegisterConfigSerializer,
        )


extension = MobileLoginRegisterConfigExtension(
    name="mobile-login-register",
    tags='login',
    scope='tenant',
    type='tenant',
    description="Mobile login and register",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="insfocus@gmail.com",
)
