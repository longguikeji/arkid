r"""
    _         ___     ._________. __     ___.___________.._________.
 /\| |/\     /   \    |  ____   \|  |  /   /|___.  .____||  _____  \
 \ ` ' /    /  ^  \   |  |__/   /|  |./   /     | |      |  |    \  \
|_     _|  /  /_\  \  |   _ ---' |       \      | |      |  |   /   、
 / , . \  /  _____  \ |  |  \  \ |  |`\   \ ___.| |.___. |  \_ /   /
 \/|_|\/ /__/     \__\\__|   `__\|__|  \___\\________ /  \______ /
"""

import logging

from arkid.auth import (
    AuthClient,

)
from arkid.authorizers import (
    AccessTokenAuthorizer,
    BasicAuthorizer,
)
from arkid.exceptions import (
    AuthAPIError,
    ArkIDAPIError,
    ArkIDConnectionError,
    ArkIDConnectionTimeoutError,
    ArkIDError,
    ArkIDSDKUsageError,
    ArkIDTimeoutError,
    NetworkError,
)
from arkid.response import ArkIDHTTPResponse, ArkIDResponse


__all__ = (
    'AuthClient',

    "ArkIDError",
    "ArkIDAPIError",
    "ArkIDSDKUsageError",

    "ArkIDConnectionError",
    "ArkIDTimeoutError",
    "ArkIDConnectionTimeoutError",
    "NetworkError",
    "AuthAPIError",

    "ArkIDResponse",
    "ArkIDHTTPResponse",

    "BasicAuthorizer",
    "AccessTokenAuthorizer",

)


VERSION = (0, 1, 0, 'final', 0)
__title__ = 'arkid-sdk'
__version_info__ = VERSION
__version__ = '.'.join(map(
    str, VERSION[:3])) + ('-{}{}'.format(VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'LongGuiKeJi'
__license__ = 'GNU'
__copyright__ = 'Copyright 2018-2020 LongGuiKeJi'

logging.getLogger("arkid").addHandler(logging.NullHandler())
