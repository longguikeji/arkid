from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    AUTHORIZATION_FAILED = ('10092', _('AUTHORIZATION_FILED', '认证失败'))
    NOT_AVAILABLE_SELECTED_IDP = ('10092-1', _('NOT_AVAILABLE_SELECTED_IDP', '无效的IDP'))
    UNSUPPORTED_BINDING = ('10092-2', _('UNSUPPORTED_BINDING', '不支持的BINDING类型'))
    UNABLE_TO_KNOW_WITCH_IDP_TO_USE = ('10092-3', _('UNABLE_TO_KNOW_WITCH_IDP_TO_USE', '无法选择IDP'))
    LOCATION_NOT_FOUND = ('10092-4', _('LOCATION_NOT_FOUND', '未找到合适的location'))
    TEMPLATE_DOES_NOT_EXISTS = ('10092-5', _('TEMPLATE_DOES_NOT_EXISTS', '模板不存在'))
    PREPARE_FOR_AUTHENTICATE_FAILED = ('10092-6', _('PREPARE_FOR_AUTHENTICATE_FAILED', '准备认证失败'))
    ACS_FAILED = ('10092-7', _('acs解析失败', 'acs解析失败'))
    UNKOWN_ERROR = ('10092-8', _('未知错误', '未知错误'))