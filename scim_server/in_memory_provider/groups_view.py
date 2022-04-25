#!/usr/bin/env python3

from scim_server.views.groups_view import GroupsViewTemplate


class InMemoryGroupsView(GroupsViewTemplate):
    @property
    def provider(self):
        from scim_server.in_memory_provider.in_memory_provider import InMemoryProvider

        return InMemoryProvider()
