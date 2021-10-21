from runtime import Runtime
from common.extension import InMemExtension
from .provider import LDAPSyncAgentProvider
from .serializers import LDAPSyncAgentSerializer


class LDAPSyncExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_authorization_agent(
            key='ldap_sync',
            name='ldap_sync',
            description='ldap_sync',
            provider=LDAPSyncAgentProvider,
            serializer=LDAPSyncAgentSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_authorization_agent(
            key='ldap_sync',
            name='ldap_sync',
            description='ldap_sync',
            provider=LDAPSyncAgentProvider,
            serializer=LDAPSyncAgentSerializer,
        )


extension = LDAPSyncExtension(
    name='ldap_sync',
    tags='ldap_sync',
    description='',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    scope='global',
    type='global',
    maintainer='rock@longguikeji.com',
)
