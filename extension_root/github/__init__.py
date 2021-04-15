from common.extension import InMemExtension

from .serializers import GithubExternalIdpSerializer
from .provider import GithubExternalIdpProvider
from .constants import KEY


class GithubExternalIdpExtension(InMemExtension):

    def start(self, runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='Github',
            description='Github',
            provider=GithubExternalIdpProvider,
            serializer=GithubExternalIdpSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)


extension = GithubExternalIdpExtension(
    name='github',
    tags='login',
    description='github as the external idP',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
