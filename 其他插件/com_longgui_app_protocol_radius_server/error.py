
from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    NOT_CONFIG = ('10001', _('NOT_CONFIG', '不存在radius服务器配置'))
    LOG_FAILURE = ('10002', _('LOG_FAILURE', '登录radius服务器失败'))