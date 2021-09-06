from common.extension import InMemExtension

from .provider import Provider
from runtime import Runtime
from .constants import KEY


class PrivacyNoticeExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):
        from extension.models import Extension

        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
        assert o is not None

        provider = Provider
        runtime.register_privacy_notice_provider(provider)
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        provider = Provider
        runtime.logout_privacy_notice_provider(provider)


extension = PrivacyNoticeExtension(
    name=KEY,
    tags='privacy_notice',
    scope='global',
    type='global',
    description='隐私声明插件',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
