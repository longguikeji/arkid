from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):
    USER_NOT_IN_WHITELIST = ('USER_NOT_IN_WHITELIST', _('该用户不可用或已封禁，如有疑问，请联系管理员'))