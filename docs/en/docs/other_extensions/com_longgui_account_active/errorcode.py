from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USER_INACTIVE = ('000001', _('账号已冻结，如有疑问，请联系管理员'))