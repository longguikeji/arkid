"""
插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime


class AuthRulesExtension(InMemExtension):
    """
    认证规则插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs): # pylint: disable=unused-argument
        pass


extension = AuthRulesExtension(
    tags='auth-rules',
    name="auth-rules",
    scope='tenant',
    type='tenant',
    description="认证规则",
    version="2.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
)
