from common.extension import InMemExtension
from .serializers import ArkIDSaasIdpSerializer, OIDCAppPlatformSerializer
from .provider import ArkIDSaasIdpProvider, OAuth2AppTypeProvider
from runtime import Runtime
from .constants import KEY


class ArkIDSaasIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="ArkID-Sass",
            description="ArkID Saas Extension",
            provider=ArkIDSaasIdpProvider,
            serializer=ArkIDSaasIdpSerializer,
        )
        runtime.register_app_type(
            key='OIDC-Platform',
            name='OpenID Connect',
            provider=OAuth2AppTypeProvider,
            serializer=OIDCAppPlatformSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="ArkID-Sass",
            description="ArkID Saas Extension",
            provider=ArkIDSaasIdpProvider,
            serializer=ArkIDSaasIdpSerializer,
        )
        runtime.logout_app_type(
            key='OIDC-Platform',
            name='OpenID Connect',
            provider=OAuth2AppTypeProvider,
            serializer=OIDCAppPlatformSerializer,
        )


extension = ArkIDSaasIdpExtension(
    tags='bind',
    name="arkid_saas",
    scope='global',
    type='global',
    description="saas arkid and local arkid bind",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="louis.law@hotmail.com",
)
