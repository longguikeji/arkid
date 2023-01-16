from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTHORIZATION_FAILED = ('10091', _('AUTHORIZATION_FILED', '认证失败'))
    EMAIL_SEND_FAILED = ('10002-5', _('email send failed', '邮件发送失败'))
    CONTACT_MANAGER = ('10002-6', _('contact manager', '发生了意外，请联系管理人员'))
    PASSWORD_IS_INCONSISTENT = ('10002-7', _('password is inconsistent', '输入密码不一致'))
    CONFIG_IS_NOT_EXISTS = ('10002-8', _('tenant extension config is not exists', '指定插件运行时配置不存在'))
    USER_NOT_IN_TENANT_ERROR = ('10030', _('can not find user in tenant', '该租户下未找到对应用户。'))
    EMAIL_CODE_MISMATCH = ('10002', _('email code mismatched', '邮箱验证码错误'))
    EMAIL_NOT_EXISTS_ERROR = ('10002-1', _('email is not exists', '邮箱号码不存在'))
    EMAIL_EMPTY = ('10002-2', _('no email provide', '邮箱号码为空'))
    EMAIL_EXISTS_ERROR = ('10002-3', _('email is already exists', '邮箱号码已存在'))
    USERNAME_EXISTS_ERROR = ('10002-9', _('username is already exists', '用户名已存在'))
    USERNAME_EMPTY = ('10002-10', _('username is empty', '用户名为空'))