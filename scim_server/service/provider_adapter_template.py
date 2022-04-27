#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException
from scim_server.service.create_request import CreateRequest
from scim_server.service.deletion_request import DeletionRequest
from scim_server.service.query_request import QueryRequest
from scim_server.service.replace_request import ReplaceRequest
from scim_server.service.retrieval_request import RetrievalRequest
from scim_server.service.update_request import UpdateRequest
from scim_server.protocol.resource_identifier import ResourceIdentifier
from scim_server.protocol.schema_identifier import SchemaIdentifier
from scim_server.protocol.query_parameters import QueryParameters
from scim_server.protocol.resource_retrieval_parameters import (
    ResourceRetrievalParamters,
)
from scim_server.service.patch import Patch


class ProviderAdapterTemplate:
    def __init__(self, provider):
        if not provider:
            raise ArgumentNullException('provider')
        self.provider = provider

    @property
    def schema_identifier(self):
        raise NotImplementedError

    def create_resouce_identifier(self, identifier):
        if not identifier:
            raise ArgumentNullException('identifier')
        result = ResourceIdentifier(self.schema_identifier, identifier)
        return result

    def create(self, request, resource, correlation_identifier):
        if request is None:
            raise ArgumentNullException('request')
        if resource is None:
            raise ArgumentNullException('resource')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')

        extensions = self.read_extensions()
        create_request = CreateRequest(
            request, resource, correlation_identifier, extensions
        )
        result = self.provider.create_async(create_request)
        return result

    def delete(self, request, identifier, correlation_identifier):
        if request is None:
            raise ArgumentNullException('request')
        if not identifier:
            raise ArgumentNullException('identifier')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')

        extensions = self.read_extensions()
        resource_identifier = self.create_resouce_identifier(identifier)
        delete_request = DeletionRequest(
            request, resource_identifier, correlation_identifier, extensions
        )
        self.provider.delete_async(delete_request)

    def get_path(self, request):
        extensions = self.read_extensions()
        if extensions is not None:
            for e in extensions:
                if e.schema_identifier == self.schema_identifier:
                    return e.path
        result = SchemaIdentifier(self.schema_identifier).find_path()
        return result

    def query(
        self,
        request,
        filters,
        requested_attribute_paths,
        excluded_attribute_paths,
        pagination_parameters,
        correlation_identifier,
    ):
        if request is None:
            raise ArgumentNullException('request')
        if requested_attribute_paths is None:
            raise ArgumentNullException('requested_attribute_paths')
        if excluded_attribute_paths is None:
            raise ArgumentNullException('excluded_attribute_paths')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')

        path = self.get_path(request)
        query_parameters = QueryParameters(
            self.schema_identifier,
            path,
            filters,
            requested_attribute_paths,
            excluded_attribute_paths,
        )
        query_parameters.pagination_parameters = pagination_parameters
        extensions = self.read_extensions()
        query_request = QueryRequest(
            request, query_parameters, correlation_identifier, extensions
        )
        result = self.provider.paginate_query_async(query_request)
        return result

    def replace(self, request, resource, correlation_identifier):
        if not request:
            raise ArgumentNullException('request')
        if not resource:
            raise ArgumentNullException('resource')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        extensions = self.read_extensions()
        replace_request = ReplaceRequest(
            request, resource, correlation_identifier, extensions
        )
        result = self.provider.replace_async(replace_request)
        return result

    def retrieve(
        self,
        request,
        identifier,
        requested_attribute_paths,
        excluded_attribute_paths,
        correlation_identifier,
    ):
        if not request:
            raise ArgumentNullException('request')
        if not identifier:
            raise ArgumentNullException('identifier')
        # if not requested_attribute_paths:
        #     raise ArgumentNullException('requested_attribute_paths')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        path = self.get_path(request)
        retrieval_parameters = ResourceRetrievalParamters(
            self.schema_identifier,
            path,
            identifier,
            requested_attribute_paths,
            excluded_attribute_paths,
        )
        extensions = self.read_extensions()
        retrieval_request = RetrievalRequest(
            request, retrieval_parameters, correlation_identifier, extensions
        )
        result = self.provider.retrieve_async(retrieval_request)
        return result

    def update(self, request, identifier, patch_request, correlation_identifier):
        if not request:
            raise ArgumentNullException('request')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        resource_identifier = self.create_resouce_identifier(identifier)
        patch = Patch(resource_identifier, patch_request)
        extensions = self.read_extensions()
        update_request = UpdateRequest(
            request, patch, correlation_identifier, extensions
        )
        self.provider.update_async(update_request)

    def read_extensions(self):
        result = []
        try:
            result = self.provider.extensions
        except NotImplementedError:
            result = []
        return result
