#!/usr/bin/env python3

from scim_server.service.provider_adapter_template import ProviderAdapterTemplate
from scim_server.schemas.schema_identifiers import SchemaIdentifiers


class Core2GroupProviderAdapter(ProviderAdapterTemplate):
    def __init__(self, provider):
        super().__init__(provider)

    @property
    def schema_identifier(self):
        return SchemaIdentifiers.Core2Group
