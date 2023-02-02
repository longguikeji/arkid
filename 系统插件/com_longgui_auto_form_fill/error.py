from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USERNAME_EXISTS = ('10001', _('用户名已经存在'))
    NOT_EXITST_APP = ('10002', _('不存在应用'))
    USERNAME_FORMAT_ERROR = ('10003', _('用户名格式错误'))
