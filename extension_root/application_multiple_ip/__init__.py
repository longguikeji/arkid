"""
插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime


class ApplicationMultipleIpExtension(InMemExtension):
    """
    桌面应用多网段IP地址处理插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):

        return super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):  # pylint: disable=unused-argument

        return super().teardown(runtime=runtime, *args, **kwargs)


extension = ApplicationMultipleIpExtension(
    tags='application_multiple_ip',
    name="application_multiple_ip",
    scope='tenant',
    type='tenant',
    description="桌面应用多网段IP地址处理插件",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
)
