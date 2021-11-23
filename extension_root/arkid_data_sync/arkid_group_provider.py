#!/usr/bin/env python3
import uuid
import json
import ldap3
from scim_server.service.provider_base import ProviderBase
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
from scim_server.schemas.core2_group import Core2Group
from .utils import get_ad_connection
from scim_server.schemas.core2_group import Core2Group
from inventory.models import User, Group


class ArkidGroupProvider(ProviderBase):
    def __init__(self, config, group_attr_map=None):
        # self.group_attr_map = group_attr_map
        self.group_attr_map = {'uuid': 'identifier', 'name': 'display_name'}
        self.config = config

    def convert_arkid_group_to_scim_group(self, arkid_group):
        group = Core2Group()
        for attr1, attr2 in self.group_attr_map.items():
            arkid_value = getattr(arkid_group, attr1)
            setattr(group, attr2, arkid_value)
        return group

    def get_all_group_from_arkid(self):
        tenant = self.config.tenant
        groups = Group.valid_objects.filter(tenant=tenant)

        all_groups = []
        for item in groups:
            group = self.convert_arkid_group_to_scim_group(item)
            all_groups.append(group)
        return all_groups

    def create_async2(self, resource, correlation_identifier):
        if not resource.identifier:
            raise BadRequestException()

        if not resource.display_name:
            raise BadRequestException()

        existing_groups = self.storage.groups.values()
        for item in existing_groups:
            if item.display_name == resource.display_name:
                raise ConflictException()
        resource_identifier = uuid.uuid4().hex
        resource.identifier = resource_identifier
        self.storage.groups[resource_identifier] = resource

        return resource

    def delete_async2(self, resource_identifier, correlation_identifier):
        if not resource_identifier.identifier:
            raise BadRequestException()
        identifier = resource_identifier.identifier

        if identifier in self.storage.groups:
            del self.storage.groups[identifier]

    def query_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            groups = self.get_all_group_from_arkid()
            return groups
        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.DisplayName:
            all_groups = self.storage.groups.values()
            group = None
            for item in all_groups:
                if item.display_name == query_filter.comparison_value:
                    group = item
                    break
            if group:
                return [group]
            else:
                return []

        raise NotSupportedException('unsupported filter')

        # for item in buffer:
        #     new_group = Core2Group()
        #     new_group.display_name = item.display_name
        #     new_group.external_identifier = item.external_identifier
        #     new_group.identifier = item.identifier
        #     new_group.members = item.members
        #     new_group.metadata = item.metadata
        #     for attr in parameters.excluded_attribute_paths:
        #         if attr == AttributeNames.Members:
        #             new_group.members = None
        # return buffer

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
        raise NotFoundException()

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
            raise NotFoundException()
