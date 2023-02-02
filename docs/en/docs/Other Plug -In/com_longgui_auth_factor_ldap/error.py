from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTHORIZATION_FAILED = ('10091', _('认证失败'))
    USER_DOES_NOT_EXIST_IN_LDAP = ('10096-1', _('未找到凭证对应的用户'))
    WRONG_PASSWORD = ('10096-2', _('密码不正确'))
    LDAP_CONNECT_FAILED = ('10096-3', _('ldap服务无法连接'))
    CONFIG_IS_NOT_EXISTS = ('10096-4', _('指定插件运行时配置不存在'))
    PASSWORD_NOT_MATCH = ('10096-5', _('两次输入的密码不一致'))