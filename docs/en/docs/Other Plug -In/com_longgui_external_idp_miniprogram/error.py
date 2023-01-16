from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    LOGIN_CONFIG_NOT_FIND = ('10042', _('not find login config', '没有找到登录配置'))
    CODE_IS_EMPTY = ('10043', _('code is empty', '没有登录的code'))