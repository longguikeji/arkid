from common.extension import InMemExtension
from .serializers import GiteeExternalIdpSerializer
from .provider import GiteeExternalIdpProvider
from .constants import KEY


class GiteeExternalIdpExtension(InMemExtension):
    def start(self, runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="Gitee",
            description="Gitee External idP",
            provider=GiteeExternalIdpProvider,
            serializer=GiteeExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = GiteeExternalIdpExtension(
    name="gitee",
    description="gitee as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="insfocus@gmail.com",
)
