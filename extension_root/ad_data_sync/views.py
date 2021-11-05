#!/usr/bin/env python3

from scim_server.views.users_view import UsersViewTemplate
from scim_server.views.groups_view import GroupsViewTemplate
from .provider import AdDataSyncProvider


class UsersView(UsersViewTemplate):
    @property
    def provider(self):
        return AdDataSyncProvider()


class GroupsView(GroupsViewTemplate):
    @property
    def provider(self):
        return AdDataSyncProvider()
