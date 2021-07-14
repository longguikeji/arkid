"""SCIM API is a set of APIs for provisioning and managing user accounts and groups.
SCIM is used by Single Sign-On (SSO) services and identity providers to manage people across a variety of tools.

"""
from .v2.client import SCIMClient  # noqa
from .v2.response import SCIMResponse  # noqa
from .v2.response import SearchUsersResponse, ReadUserResponse  # noqa
from .v2.response import SearchGroupsResponse, ReadGroupResponse  # noqa
from .v2.user import User  # noqa
from .v2.group import Group  # noqa
