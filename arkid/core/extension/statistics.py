
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.event import GET_STATISTICS_CHARTS


class StatisticsExtension(Extension):

    TYPE = "statistics"

    @property
    def type(self):
        return StatisticsExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(GET_STATISTICS_CHARTS, self.get_charts)

    def get_charts(self, event, **kwargs):
        """获取统计图表
        """
        return []

