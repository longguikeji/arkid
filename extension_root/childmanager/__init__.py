from common.extension import InMemExtension
from .constants import KEY
from runtime import Runtime
from extension_root.childmanager.provider import ChildManagerProvider


class ChildManagerExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None
        provider = ChildManagerProvider()
        runtime.register_childmanagerconfig_provider(
            provider
        )
        super().start(runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = ChildManagerProvider()
        runtime.logout_childmanagerconfig_provider(
            provider
        )


extension = ChildManagerExtension(
    name=KEY,
    tags='admin',
    scope='tenant',
    type='tenant',
    description='子管理员',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='hanbin@jinji-inc.com',
)
