from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USER_NOT_IN_TENANT_ERROR = ('10030', _('can not find user in tenant', '该租户下未找到对应用户。'))
    SMS_CODE_MISMATCH = ('10002', _('sms code mismatched', '手机验证码错误'))
    MOBILE_NOT_EXISTS_ERROR = ('10021', _('mobile is not exists', '电话号码不存在'))
    MOBILE_EMPTY = ('10022', _('no mobile provide', '手机号码为空'))
    MOBILE_EXISTS_ERROR = ('10023', _('mobile is already exists', '手机号码已存在'))