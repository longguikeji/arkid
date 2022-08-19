from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USERNAME_PASSWORD_MISMATCH = ('10001-1', _('用户名或密码错误'))
    CONTACT_MANAGER = ('10001-5', _('发生了意外，请联系管理人员'))
    USERNAME_EMPTY = ('10001-6', _('用户名为空'))
    ALL_USER_FLAG_LACK_FIELD = ('10001-7', _('所有用户标识至少填一个'))
    FIELD_USER_EXISTS = ('10001-8', _('{field}字段和已经有的用户重复'))
    PASSWORD_STRENGTH_LACK = ('10001-9', _('密码强度不够'))
    TWO_TIME_PASSWORD_MISMATCH = ('10001-10', _('两次输入的密码不同'))
    OLD_PASSWORD_ERROR = ('10001-11', _('旧密码不匹配'))