"""
插件处理
"""
from common.extension import InMemExtension
from runtime import Runtime


class AppMarketManageExtension(InMemExtension):
    """
    认证规则插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):

        return super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):  # pylint: disable=unused-argument

        return super().teardown(runtime=runtime, *args, **kwargs)


extension = AppMarketManageExtension(
    tags='app_market_manage',
    name="app_market_manage",
    scope='tenant',
    type='tenant',
    description="桌面应用管理，即是否允许应用显示于用户桌面",
    version="2.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="guancyxx@guancyxx.cn",
)