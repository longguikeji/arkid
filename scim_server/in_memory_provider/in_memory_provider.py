#!/usr/bin/env python3
from scim_server.service.provider_base import ProviderBase
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.in_memory_provider.in_memory_user_provider import InMemoryUserProvider
from scim_server.in_memory_provider.in_memory_group_provider import InMemoryGroupProvider

class InMemoryProvider(ProviderBase):

    TypeSchema = []
    Types = []

    def __init__(self):
        self.group_provider = InMemoryGroupProvider()
        self.user_provider = InMemoryUserProvider()

    @property
    def resource_types(self):
        return InMemoryProvider.Types

    @property
    def schema(self):
        return InMemoryProvider.TypeSchema

    def create_async2(self, resource, correlation_identifier):
        if isinstance(resource, Core2EnterpriseUser):
            return self.user_provider.create_async2(resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.group_provider.create_async2(resource, correlation_identifier)

        raise NotImplementedError()

    def delete_async2(self, resource_identifier, correlation_identifier):
        if (
            resource_identifier.schema_identifier
            == SchemaIdentifiers.Core2EnterpriseUser
        ):
            return self.user_provider.delete_async2(
                resource_identifier, correlation_identifier
            )

        if resource_identifier.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.delete_async2(
                resource_identifier, correlation_identifier
            )

        raise NotImplementedError()

    def query_async2(self, parameters, correlation_identifier):
        if parameters.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser:
            return self.user_provider.query_async2(parameters, correlation_identifier)

        if parameters.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.query_async2(parameters, correlation_identifier)

        raise NotImplementedError()

    def replace_async2(self, resource, correlation_identifier):
        if isinstance(resource, Core2EnterpriseUser):
            return self.user_provider.replace_async2(resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.group_provider.replace_async2(resource, correlation_identifier)

    def retrieve_async2(self, parameters, correlation_identifier):
        if parameters.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser:
            return self.user_provider.retrieve_async2(
                parameters, correlation_identifier
            )

        if parameters.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.retrieve_async2(
                parameters, correlation_identifier
            )

        raise NotImplementedError()

    def update_async2(self, patch, correlation_identifier):
        if not patch:
            raise ArgumentNullException('patch')
        if not patch.resource_identifier.identifier:
            raise ArgumentException('patch')
        if not patch.resource_identifier.schema_identifier:
            raise ArgumentException('patch')

        if (
            patch.resource_identifier.schema_identifier
            == SchemaIdentifiers.Core2EnterpriseUser
        ):
            return self.user_provider.update_async2(patch, correlation_identifier)

        if patch.resource_identifier.schema_identifier == SchemaIdentifiers.Core2Group:
            return self.group_provider.update_async2(patch, correlation_identifier)

        raise NotImplementedError()
