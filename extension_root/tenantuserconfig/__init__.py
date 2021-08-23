from common.extension import InMemExtension
from .constants import KEY
from runtime import Runtime
from .provider import TenantUserConfigIdpProvider
from .serializers import MiniProgramExternalIdpSerializer


class TenantUserConfigExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None
        provider = TenantUserConfigIdpProvider()
        runtime.register_tenantuserconfig_provider(
            provider
        )
        super().start(runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = TenantUserConfigIdpProvider()
        runtime.logout_tenantuserconfig_provider(
            provider
        )


extension = TenantUserConfigExtension(
    name='tenantuserconfig',
    tags='config',
    scope='tenant',
    type='tenant',
    description='租户个人配置',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
