from runtime import Runtime
from common.extension import InMemExtension
from .provider import LDAPAuthorizationAgentProvider
from .serializers import LDAPAuthorizationAgentSerializer


class LDAPAuthExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_authorization_agent(
            key='ldap_auth',
            name='ldap_auth',
            description='ldap_auth',
            provider=LDAPAuthorizationAgentProvider,
            serializer=LDAPAuthorizationAgentSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_authorization_agent(
            key='ldap_auth',
            name='ldap_auth',
            description='ldap_auth',
            provider=LDAPAuthorizationAgentProvider,
            serializer=LDAPAuthorizationAgentSerializer,
        )


extension = LDAPAuthExtension(
    name='ldap_auth',
    tags='ldap_auth',
    description='',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    scope='global',
    type='global',
    maintainer='rock@longguikeji.com',
)
