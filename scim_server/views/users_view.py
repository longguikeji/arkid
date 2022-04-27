#!/usr/bin/env python3

from scim_server.views.view_template import ViewTemplate
from scim_server.exceptions import NotImplementedException


class UsersViewTemplate(ViewTemplate):
    @property
    def model_cls(self):
        from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser

        return Core2EnterpriseUser

    @property
    def provider(self):
        raise NotImplementedException()

    @property
    def adapter_provider(self):
        from scim_server.service.core2_enterprise_user_provider_adapter import (
            Core2EnterpriseUserProviderAdapter,
        )

        # TODO deliver parameter from view to provider
        result = Core2EnterpriseUserProviderAdapter(self.provider)
        return result
