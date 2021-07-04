from common.extension import InMemExtension
from .constants import KEY
from .provider import SAML2IDPAppTypeProvider
from .serializers import SAMLasIDPSerializer

class SAML2IdpExtension(InMemExtension):
    def start(self, runtime, *args, **kwargs):
        runtime.register_authorization_server(
            id='saml2idp',
            name='SAML2.0 IDP',
            description='SAML2.0 IDP',
        )
        runtime.register_app_type(
            key='saml2idp',
            name='SAML2.0 IDP',
            provider=SAML2IDPAppTypeProvider,
            serializer=SAMLasIDPSerializer
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = SAML2IdpExtension(
    tags='saml',
    name="saml2idp",
    scope='tenant',
    type='tenant',
    description="SAML AS Idp",
    version="2.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
)
