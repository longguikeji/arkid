from enum import Enum
from arkid.core.translation import gettext_default as _


class ScanErrorCode(Enum):

    QRCODE_ID_NOT_FOUND_ERROR = (
        "10060-10",
        _("QRCode ID Not Found", "没有找到QRCode ID"),
    )
    QRCODE_ID_EXPIRED_ERROR = (
        "10060-20",
        _("QRCode ID Has Expired", "QRCode ID已经过期"),
    )
