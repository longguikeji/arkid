#!/usr/bin/env python3

from scim_server.views.view_template import ViewTemplate


class GroupsView(ViewTemplate):
    @property
    def model_cls(self):
        from scim_server.schemas.core2_group import Core2Group

        return Core2Group

    @property
    def provider(self):
        # from scim_server.provider.in_memory_provider import InMemoryProvider
        from scim_server.mssql_provider.mssql_provider import MssqlProvider

        return MssqlProvider()

    @property
    def adapter_provider(self):
        from scim_server.service.core2_group_provider_adapter import (
            Core2GroupProviderAdapter,
        )

        result = Core2GroupProviderAdapter(self.provider)
        return result
