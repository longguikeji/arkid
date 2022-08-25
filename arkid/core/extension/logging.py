
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.event import REQUEST_RESPONSE_LOGGGING


class LoggingExtension(Extension):

    TYPE = "logging"

    @property
    def type(self):
        return LoggingExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(REQUEST_RESPONSE_LOGGGING, self.save)

    @abstractmethod
    def save(self, event, **kwargs):
        """保存日志
        """
        pass

