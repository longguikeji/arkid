#!/usr/bin/env python3
from scim_server.schemas.bulk_requests_feature import BulkRequestsFeature
from scim_server.schemas.core2_service_configuration import Core2ServiceConfiguration
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.service.query_response import QueryResponse


class ProviderBase:
    BulkFeatureSupport = BulkRequestsFeature.create_unsupported_feature()
    TypeSchema = []
    ServiceConfiguration = Core2ServiceConfiguration(
        BulkFeatureSupport, False, True, False, True, False
    )
    Types = []

    @property
    def accept_large_objects(self):
        pass

    @property
    def configuration(self):
        return ProviderBase.ServiceConfiguration

    @property
    def extensions(self):
        return None

    @property
    def group_deserialization_behavior(self):
        return None

    @property
    def patch_request_deserialization_behavior(self):
        return None

    @property
    def resource_types(self):
        return ProviderBase.Types

    @property
    def schema(self):
        return ProviderBase.TypeSchema

    @property
    def user_deserialization_behavior(self):
        return None

    def create_async2(self, resource, correlation_identifier):
        pass

    def create_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.create_async2(request.payload, request.correlation_identifier)
        return result

    def delete_async2(self, resource_identifier, correlation_identifier):
        pass

    def delete_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.delete_async2(request.payload, request.correlation_identifier)
        return result

    def paginate_query_async(self, request):
        if not request:
            raise ArgumentNullException('request')

        resources = self.query_async(request)
        result = QueryResponse(resources)
        result.total_results = result.items_per_page = len(resources)
        result.start_index = 1 if resources else None
        return result

    def process_async(self):
        pass

    def query_async2(self, parameters, correlation_identifier):
        pass

    def query_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.query_async2(request.payload, request.correlation_identifier)
        return result

    def replace_async2(self, resource, correlation_identifier):
        pass

    def replace_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.replace_async2(request.payload, request.correlation_identifier)
        return result

    def retrieve_async2(self, parameters, correlation_identifier):
        pass

    def retrieve_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.retrieve_async2(request.payload, request.correlation_identifier)
        return result

    def update_async2(self, patch, correlation_identifier):
        pass

    def update_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')
        result = self.update_async2(request.payload, request.correlation_identifier)
        return result
