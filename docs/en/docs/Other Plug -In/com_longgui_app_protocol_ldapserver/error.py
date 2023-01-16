from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTHCODE_NOT_MATCH = ('10090', _('AUTH_EXTENSION_IS_DISACTIVELY', '认证插件未启用'))
    DN_NOT_MATCH = ('10090-1', _('DN_NOT_MATCH', '认证域名不匹配'))
    NO_ACTIVE_EXTENSION_SETTINGS = ('10090-2', _('NO_ACTIVE_EXTENSION_SETTINGS', '没有已启用的插件服务'))
    UNSUPPORTED_SCOPE = ('10090-3', _('UNSUPPORTED_SCOPE', '不支持的查询范围'))