#!/usr/bin/env python3
import uuid
import json
import ldap3
from scim_server.service.provider_base import ProviderBase
from scim_server.in_memory_provider.in_memory_storage import Instance
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
from ldap3 import Server, Connection
from data_sync.models import DataSyncConfig
from .utils import get_ad_connection
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser


class AdUserProvider(ProviderBase):
    user_object_class = 'user'
    group_object_class = 'group'
    ou_object_class = 'organizationalUnit'

    def __init__(self, config, user_attr_map=None):
        # self.user_attr_map = user_attr_map
        self.user_attr_map = {'objectGUID': 'identifier', 'cn': 'user_name'}
        self.root_dn = config.get('root_dn')
        self.config = config
        self._connection = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = get_ad_connection(self.config)
            return self._connection
        else:
            return self._connection

    def convert_ad_user_to_scim_user(self, ad_user):
        ad_user_attrs = ad_user['attributes']
        user = Core2EnterpriseUser()
        for attr1, attr2 in self.user_attr_map.items():
            ad_value = ad_user_attrs.get(attr1)
            setattr(user, attr2, ad_value)
        return user

    def get_all_users_from_ldap(self):
        search_base = self.root_dn
        search_filter = f'(objectClass={self.user_object_class})'
        res = self.connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        if not res:
            return []
        all_users = []
        entries = json.loads(self.connection.response_to_json())['entries']
        for item in entries:
            user = self.convert_ad_user_to_scim_user(item)
            all_users.append(user)
        return all_users

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
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            all_users = self.get_all_users_from_ldap()
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
