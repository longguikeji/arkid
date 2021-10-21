#!/usr/bin/env python
import uuid
from scim_server.service.provider_base import ProviderBase
from scim_server.provider.in_memory_storage import Instance
from scim_server.exceptions import (
    ArgumentException,
    ArgumentNullException,
    BadRequestException,
    ConflictException,
    NotSupportedException,
    NotFoundException,
)
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.schemas.attribute_names import AttributeNames


class InMemoryUserProvider(ProviderBase):
    def __init__(self):
        self.storage = Instance

    def create_async2(self, resource, correlation_identifier):
        if resource.identifier is not None:
            raise BadRequestException()

        if not resource.user_name:
            raise BadRequestException()

        existing_users = self.storage.users.values()
        for item in existing_users:
            if item.user_name == resource.user_name:
                raise ConflictException()
        resource_identifier = uuid.uuid4().hex
        resource.identifier = resource_identifier
        self.storage.users[resource_identifier] = resource

        return resource

    def delete_async2(self, resource_identifier, correlation_identifier):
        if not resource_identifier.identifier:
            raise BadRequestException()
        identifier = resource_identifier.identifier

        if identifier in self.storage.users:
            del self.storage.users[identifier]

    def query_async2(self, parameters, correlation_identifier):
        if parameters is None:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if  parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            all_users = self.storage.users.values()
            return all_users

        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.UserName:
            all_users = self.storage.users.values()
            user = None
            for item in all_users:
                if item.user_name == query_filter.comparison_value:
                    user = item
                    break
            if user:
                return [user]
            else:
                return []

        if query_filter.attribute_path == AttributeNames.ExternalIdentifier:
            all_users = self.storage.users.values()
            user = None
            for item in all_users:
                if item.external_identifier == query_filter.comparison_value:
                    user = item
                    break
            if user:
                return [user]
            else:
                return []

        raise NotSupportedException('unsupported filter')

    def replace_async2(self, resource, correlation_identifier):
        if not resource.identifier:
            raise BadRequestException()
        if not resource.user_name:
            raise BadRequestException()

        existing_users = self.storage.users.values()
        for item in existing_users:
            if item.user_name == resource.user_name:
                raise ConflictException()
        if resource.identifier not in self.storage.users:
            raise NotFoundException()

        self.storage.users[resource.identifier] = resource
        return resource

    def retrieve_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if not parameters.resource_identifier.identifier:
            raise ArgumentNullException('parameters')

        result = None
        identifier = parameters.resource_identifier.identifier
        if identifier in self.storage.users:
            return self.storage.users[identifier]
        raise NotFoundException(identifier)

    def update_async2(self, patch, correlation_identifier):
        if not patch:
            raise ArgumentNullException('patch')
        if not patch.resource_identifier:
            raise ArgumentException('Invalid patch')
        if not patch.resource_identifier.identifier:
            raise ArgumentException('invalid patch')
        if not patch.patch_request:
            raise ArgumentException('invalid patch')
        user = self.storage.users.get(patch.resource_identifier.identifier)
        if user:
            user.apply(patch.patch_request)
        else:
            raise NotFoundException(patch.resource_identifier.identifier)
