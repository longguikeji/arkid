from common.extension import InMemExtension
from .serializers import LdapLoginConfigSerializer
from .provider import LdapLoginConfigProvider
from runtime import Runtime
from .constants import KEY


class LdapLoginConfigExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_login_register_config(
            key=KEY,
            name="ldap_login",
            description="Ldap login config",
            provider=LdapLoginConfigProvider,
            serializer=LdapLoginConfigSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_login_register_config(
            key=KEY,
            name="ldap_login",
            description="Ldap login config",
            provider=LdapLoginConfigProvider,
            serializer=LdapLoginConfigSerializer,
        )


extension = LdapLoginConfigExtension(
    name=KEY,
    tags='login',
    scope='tenant',
    type='tenant',
    description="Ldap login",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="insfocus@gmail.com",
)
