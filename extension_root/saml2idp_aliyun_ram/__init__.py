"""
SAML 2.0  插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime
from .constants import KEY
from .provider import SAML2IDPAppTypeProvider
from .serializers import SAMLasIDPAliyunRamSerializer


class SAML2IdpAliyunRamExtension(InMemExtension):
    """
    SAML2 IDP插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_authorization_server(
            id=KEY,
            name=KEY,
            description='SAML2.0 IDP 阿里云用户 SSO',
        )
        runtime.register_app_type(
            key=KEY,
            name=KEY,
            provider=SAML2IDPAppTypeProvider,
            serializer=SAMLasIDPAliyunRamSerializer
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs): # pylint: disable=unused-argument
        runtime.logout_authorization_server(
            id=KEY,
            name=KEY,
            description='SAML2.0 IDP 阿里云用户 SSO',
        )
        runtime.logout_app_type(
            key=KEY,
            name=KEY,
            provider=SAML2IDPAppTypeProvider,
            serializer=SAMLasIDPAliyunRamSerializer
        )


extension = SAML2IdpAliyunRamExtension(
    tags='saml',
    name=KEY,
    scope='tenant',
    type='tenant',
    description='SAML2.0 IDP 阿里云用户 SSO',
    version="2.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="guancyxx@guancyxx.cn",
)
