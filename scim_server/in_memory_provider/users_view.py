#!/usr/bin/env python3

from scim_server.views.users_view import UsersViewTemplate


class InMemoryUsersView(UsersViewTemplate):
    @property
    def provider(self):
        from scim_server.in_memory_provider.in_memory_provider import InMemoryProvider

        return InMemoryProvider()
