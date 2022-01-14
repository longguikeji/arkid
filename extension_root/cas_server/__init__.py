from runtime import Runtime
from common.extension import InMemExtension, ExtensionBaseSerializer
from .provider import CasAppTypeProvider
from .serializers import CasAppSerializer


class CasServerExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        # Contribute OAuth Authentication Server & parameters
        runtime.register_app_type(
            key='Cas',
            name='Cas',
            provider=CasAppTypeProvider,
            serializer=CasAppSerializer
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        # Contribute OAuth Authentication Server & parameters
        runtime.logout_app_type(
            key='Cas',
            name='Cas',
            provider=CasAppTypeProvider,
            serializer=CasAppSerializer
        )

extension = CasServerExtension(
    scope='tenant',
    type='tenant',
    tags='Cas',
    name='cas_server',
    description='Arkid cas server',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='hanbin@jinji-inc.com',
)
