from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    USER_NOT_IN_TENANT_ERROR = ('10030', _('can not find user in tenant', '该租户下未找到对应用户。'))
    SMS_CODE_MISMATCH = ('10002', _('sms code mismatched', '手机验证码错误'))
    MOBILE_NOT_EXISTS_ERROR = ('10002-1', _('mobile is not exists', '电话号码不存在'))
    MOBILE_EMPTY = ('10002-2', _('no mobile provide', '手机号码为空'))
    MOBILE_EXISTS_ERROR = ('10002-3', _('mobile is already exists', '手机号码已存在'))
    SMS_EXTENSION_NOT_EXISTS = ('10002-4', _('sms extension is not running', '短信插件未启用'))
    SMS_SEND_FAILED = ('10002-5', _('sms send failed', '短信发送失败'))
    CONTACT_MANAGER = ('10002-6', _('contact manager', '发生了意外，请联系管理人员'))
    PASSWORD_IS_INCONSISTENT = ('10002-7', _('password is inconsistent', '输入密码不一致'))
