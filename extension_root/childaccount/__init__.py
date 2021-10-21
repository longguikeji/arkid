from common.extension import InMemExtension
from .constants import KEY
from runtime import Runtime
from extension_root.childaccount.provider import ChildAccountProvider


class ChildAccountExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None
        provider = ChildAccountProvider()
        runtime.register_childaccountconfig_provider(
            provider
        )
        super().start(runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = ChildAccountProvider()
        runtime.logout_childaccountconfig_provider(
            provider
        )


extension = ChildAccountExtension(
    name=KEY,
    tags='user',
    scope='global',
    type='global',
    description='子账户',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
