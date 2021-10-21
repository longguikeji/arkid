#!/usr/bin/env python3

from scim_server.views.view_template import ViewTemplate
from scim_server.provider.in_memory_provider import InMemoryProvider

# from scim_server.service.core2


class UsersView(ViewTemplate):
    @property
    def model_cls(self):
        from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser

        return Core2EnterpriseUser

    @property
    def provider(self):
        from scim_server.mssql_provider.mssql_provider import MssqlProvider

        return MssqlProvider()

    @property
    def adapter_provider(self):
        from scim_server.service.core2_enterprise_user_provider_adapter import (
            Core2EnterpriseUserProviderAdapter,
        )

        result = Core2EnterpriseUserProviderAdapter(self.provider)
        return result
