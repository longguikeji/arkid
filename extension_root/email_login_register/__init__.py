from common.extension import InMemExtension
from .serializers import EmailLoginRegisterConfigSerializer
from .provider import EmailLoginRegisterConfigProvider
from runtime import Runtime
from .constants import KEY


class EmailLoginRegisterConfigExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_login_register_config(
            key=KEY,
            name="email_login_register",
            description="Email login and register",
            provider=EmailLoginRegisterConfigProvider,
            serializer=EmailLoginRegisterConfigSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_login_register_config(
            key=KEY,
            name="email_login_register",
            description="Email login register config",
            provider=EmailLoginRegisterConfigProvider,
            serializer=EmailLoginRegisterConfigSerializer,
        )


extension = EmailLoginRegisterConfigExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="Email login and register",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="fanhe@longguikeji.com",
)
