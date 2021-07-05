from common.extension import InMemExtension
from .serializers import SAML2SPSerializer
from .provider import SAML2SPExternalIdpProvider
from .constants import KEY


class SAML2SPExtension(InMemExtension):
    def start(self, runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='saml2sp',
            description='saml 2.0',
            provider=SAML2SPExternalIdpProvider,
            serializer=SAML2SPSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = SAML2SPExtension(
    tags='saml2',
    name="saml2sp",
    scope='tenant',
    type='tenant',
    description="SAML2.0 as SP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司"
)
