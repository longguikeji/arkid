from enum import Enum
from arkid.core.translation import gettext_default as _

class ErrorCode(Enum):

    FIELDS_VALUE_REPEAT = ('10001-1', _('{field}字段{value}和已经有的用户重复'))