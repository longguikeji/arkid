from enum import Enum
from arkid.core.translation import gettext_default as _


class OTPErrorCode(Enum):

    NONE_OTP_CODE_ERROR = (
        "10050-10",
        _("None OTP Code Found", "请输入OTP一次性密码"),
    )
    OTP_CODE_MISMATCH_ERROR = (
        "10050-20",
        _("OTP Code Mismatch", "OTP代码不一致"),
    )
