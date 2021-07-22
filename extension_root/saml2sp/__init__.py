"""
SAML 2.0  插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime
from .constants import KEY
from .provider import Saml2SPExternalIdpProvider
from .serializers import SAML2SPSerializer


class SAML2SPExtension(InMemExtension):
    """
    SAML2 IDP插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='saml2.0 service provider',
            description='SAML2.0 服务提供商',
            provider=Saml2SPExternalIdpProvider,
            serializer=SAML2SPSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs): # pylint: disable=unused-argument
        runtime.logout_external_idp(
            key=KEY,
            name='saml2.0 service provider',
            description='SAML2.0 服务提供商',
            provider=Saml2SPExternalIdpProvider,
            serializer=SAML2SPSerializer,
        )


extension = SAML2SPExtension(
    name='saml2sp',
    tags='login',
    scope='tenant',
    type='tenant',
    description='saml2sp',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='北京龙归科技有限公司'
)
