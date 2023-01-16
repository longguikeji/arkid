from enum import Enum
from arkid.core.translation import gettext_default as _


class WebauthnErrorCode(Enum):

    REGISTRATION_VERIFICATION_ERROR = (
        "10001-30",
        _("Webauthn verification failed", "Webauthn注册校验凭证失败"),
    )
    AUTHENTICATION_VERIFICATION_ERROR = (
        "10001-31",
        _("Webauthn authentication failed", "Webauthn登录校验凭证失败"),
    )
    AUTHENTICATION_NO_CREDENTIAL_ERROR = (
        "10001-32",
        _("That username has no registered credentials", "该用户不存在对应的认证凭证"),
    )
    CREDENTIAL_DELETE_ERROR = (
        "10001-33",
        _("Can not delete, should keep credential to login", "请确保已设置密码，否则不能删除此凭证"),
    )
