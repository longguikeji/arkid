#!/usr/bin/env python3

from scim_server.views.users_view import UsersViewTemplate


class UsersView(UsersViewTemplate):
    @property
    def provider(self):
        from scim_server.mssql_provider.mssql_provider import MssqlProvider

        return MssqlProvider()
