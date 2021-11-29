from common.extension import InMemExtension
from .serializers import PasswordLoginRegisterConfigSerializer
from .provider import PasswordLoginRegisterConfigProvider
from runtime import Runtime
from .constants import KEY


class PasswordLoginRegisterConfigExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_login_register_config(
            key=KEY,
            name="password_login_register",
            description="Password login and register",
            provider=PasswordLoginRegisterConfigProvider,
            serializer=PasswordLoginRegisterConfigSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_login_register_config(
            key=KEY,
            name="password_login_register",
            description="Password login register config",
            provider=PasswordLoginRegisterConfigProvider,
            serializer=PasswordLoginRegisterConfigSerializer,
        )


extension = PasswordLoginRegisterConfigExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="Password login and register",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="fanhe@longguikeji.com",
)
