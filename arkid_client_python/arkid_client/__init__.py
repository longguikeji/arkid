r"""
    _         ___     ._________. __     ___.___________.._________.
 /\| |/\     /   \    |  ____   \|  |  /   /|___.  .____||  _____  \
 \ ` ' /    /  ^  \   |  |__/   /|  |./   /     | |      |  |    \  \
|_     _|  /  /_\  \  |   _ ---' |       \      | |      |  |   /   、
 / , . \  /  _____  \ |  |  \  \ |  |`\   \ ___.| |.___. |  \_ /   /
 \/|_|\/ /__/     \__\\__|   `__\|__|  \___\\________ /  \______ /
"""

import logging

from arkid_client.auth import (
    AuthClient,
    ConfidentialAppAuthClient,
)
from arkid_client.authorizers import (
    AccessTokenAuthorizer,
    BasicAuthorizer,
    NullAuthorizer
)
from arkid_client.user import UserClient
from arkid_client.org import OrgClient
from arkid_client.node import NodeClient
from arkid_client.infrastructure import InfrastructureClient
from arkid_client.ucenter import UcenterClient
from arkid_client.app import AppClient
from arkid_client.perm import PermClient

from arkid_client.exceptions import (
    AuthAPIError,
    ArkIDAPIError,
    ArkIDConnectionError,
    ArkIDConnectionTimeoutError,
    ArkIDError,
    ArkIDSDKUsageError,
    ArkIDTimeoutError,
    NetworkError,
)
from arkid_client.client import ArkIDClient
from arkid_client.response import ArkIDHTTPResponse, ArkIDResponse
from arkid_client.version import (
    __version__,
    __author__,
    __copyright__,
    __license__,
    __version_info__,
    __title__,
)

__all__ = (
    '__version__',
    '__author__',
    '__copyright__',
    '__license__',
    '__version_info__',
    '__title__',

    'ArkIDClient',
    'AuthClient',
    'ConfidentialAppAuthClient',
    'UserClient',
    'OrgClient',
    'NodeClient',
    'InfrastructureClient',
    'UcenterClient',
    'AppClient',
    'PermClient',

    'ArkIDError',
    'ArkIDAPIError',
    'ArkIDSDKUsageError',
    'ArkIDConnectionError',
    'ArkIDTimeoutError',
    'ArkIDConnectionTimeoutError',
    'NetworkError',
    'AuthAPIError',
    'ArkIDResponse',
    'ArkIDHTTPResponse',
    'BasicAuthorizer',
    'NullAuthorizer',
    'AccessTokenAuthorizer',
)

logging.getLogger("arkid_client").addHandler(logging.NullHandler())
