
from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    NOT_CONFIG = ('10001', _('NOT_CONFIG', '没有该应用的多账号配置'))
    AUHENTICATION_FAILED = ('10002', _('AUHENTICATION_FAILED', '应用账号绑定失败，请联系应用开发者或管理员'))