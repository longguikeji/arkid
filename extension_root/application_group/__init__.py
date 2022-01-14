"""
插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime

class ApplicationGroupExtension(InMemExtension):
    """
    应用内账号插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):

        return super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs): # pylint: disable=unused-argument

        return super().teardown(runtime=runtime, *args, **kwargs)


extension = ApplicationGroupExtension(
    tags='application_group',
    name="application_group",
    scope='tenant',
    type='tenant',
    description="应用内账号",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
)
