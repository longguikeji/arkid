from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USERNAME_IN_BLACKLIST = ('USERNAME_IN_BLACKLIST', _('该用户名不可用或已封禁，如有疑问，请联系管理员'))
    MOBILE_IN_BLACKLIST = ('MOBILE_IN_BLACKLIST', _('该电话号码不可用或已封禁，如有疑问，请联系管理员'))
    EMAIL_IN_BLACKLIST = ('EMAIL_IN_BLACKLIST', _('该邮箱不可用或已封禁，如有疑问，请联系管理员'))