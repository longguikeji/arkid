#!/usr/bin/env python3

from scim_server.views.groups_view import GroupsViewTemplate
from scim_server.exceptions import NotImplementedException


class GroupsView(GroupsViewTemplate):
    @property
    def provider(self):
        from scim_server.mssql_provider.mssql_provider import MssqlProvider

        return MssqlProvider()
