from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTH_FAIL_TIMES_OVER_LIMITED = ('10050', _('认证失败次数超出限制，需刷新页面'))