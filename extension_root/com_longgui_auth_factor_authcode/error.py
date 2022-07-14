from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTHCODE_NOT_MATCH = ('10040', _('code is not match', '验证码不匹配'))