#!/usr/bin/env python3
from curses import meta
from scim_server.schemas.service_configuration_base import ServiceConfigurationBase
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.core2_metadata import Core2Metadata
from scim_server.schemas.types import Types
from scim_server.schemas.feature import Feature
from typing import Optional


class Core2ServiceConfiguration(ServiceConfigurationBase):
    meta: Optional[Core2Metadata]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = Core2Metadata(resourceType=Types.ServiceProviderConfiguration)
        self.add_schema(SchemaIdentifiers.Core2ServiceConfiguration)

    # def __init__(
    #     self,
    #     bulk_requests_support,
    #     supports_entity_tags,
    #     supports_filtering,
    #     supports_password_change,
    #     supports_patching,
    #     supports_sorting,
    # ):
    #     super().__init__()
    #     self.add_schema(SchemaIdentifiers.Core2ServiceConfiguration)
    #     self.metadata = Core2Metadata()
    #     self.metadata.resource_type = Types.ServiceProviderConfiguration

    #     self.bulk_requests = bulk_requests_support
    #     self.entity_tags = Feature(supports_entity_tags)
    #     self.filtering = Feature(supports_filtering)
    #     self.password_change = Feature(supports_password_change)
    #     self.patching = Feature(supports_patching)
    #     self.sorting = Feature(supports_sorting)

    # @property
    # def metadata(self):
    #     return self._metadata

    # @metadata.setter
    # def metadata(self, value):
    #     self._metadata = value
