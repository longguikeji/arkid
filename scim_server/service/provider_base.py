#!/usr/bin/env python3
from scim_server.schemas.bulk_requests_feature import BulkRequestsFeature
from scim_server.schemas.core2_service_configuration import Core2ServiceConfiguration
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.service.query_response import QueryResponse
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group


class ProviderBase:
    TypeSchema = []
    config_data = {
        "authenticationSchemes": [
            {"type": "oauth2", "name": "OAuth2", "description": "OAuth2"}
        ],
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "etag": {"supported": False},
        "filter": {"supported": True, "maxResults": 200},
        "changePassword": {"supported": False},
        "patch": {"supported": True},
        "sort": {"supported": False},
    }
    ServiceConfiguration = Core2ServiceConfiguration(**config_data)
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

    def create_user(self, request, resource, correlation_identifier):
        pass

    def create_group(self, request, resource, correlation_identifier):
        pass

    def create_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        resource = request.payload
        correlation_identifier = request.correlation_identifier
        if isinstance(resource, Core2EnterpriseUser):
            return self.create_user(request.request, resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.create_group(request.request, resource, correlation_identifier)

    def delete_user(self, request, resource_identifier, correlation_identifier):
        pass

    def delete_group(self, request, resource_identifier, correlation_identifier):
        pass

    def delete_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        resource = request.payload
        correlation_identifier = request.correlation_identifier
        if isinstance(resource, Core2EnterpriseUser):
            return self.delete_user(request.request, resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.delete_group(request.request, resource, correlation_identifier)

    def paginate_query_async(self, request):
        if not request:
            raise ArgumentNullException('request')

        resources = self.query_async(request)
        result = QueryResponse(Resources=resources)
        result.totalResults = result.itemsPerPage = len(resources)
        result.startIndex = 1 if resources else None
        return result

    def query_users(self, request, parameters, correlation_identifier):
        pass

    def query_groups(self, request, parameters, correlation_identifier):
        pass

    def query_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        parameters = request.payload
        correlation_identifier = request.correlation_identifier
        if parameters.path == 'Users':
            return self.query_users(request.request, parameters, correlation_identifier)

        if parameters.path == 'Groups':
            return self.query_groups(
                request.request, parameters, correlation_identifier
            )

    def replace_user(self, request, resource, correlation_identifier):
        pass

    def replace_group(self, request, resource, correlation_identifier):
        pass

    def replace_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        resource = request.payload
        correlation_identifier = request.correlation_identifier
        if isinstance(resource, Core2EnterpriseUser):
            return self.replace_user(request.request, resource, correlation_identifier)

        if isinstance(resource, Core2Group):
            return self.replace_group(request.request, resource, correlation_identifier)

    def retrieve_user(self, request, parameters, correlation_identifier):
        pass

    def retrieve_group(self, request, parameters, correlation_identifier):
        pass

    def retrieve_async(
        self,
        request,
    ):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        parameters = request.payload
        correlation_identifier = request.correlation_identifier
        if parameters.path == 'Users':
            return self.retrieve_user(
                request.request, parameters, correlation_identifier
            )

        if parameters.path == 'Groups':
            return self.retrieve_group(
                request.request, parameters, correlation_identifier
            )

    def update_user(self, request, patch, correlation_identifier):
        pass

    def update_group(self, request, patch, correlation_identifier):
        pass

    def update_async(self, request):
        if not request:
            raise ArgumentNullException('request')
        if not request.payload:
            raise ArgumentException('Invalid Request')
        if not request.correlation_identifier:
            raise ArgumentException('Invalid Request')

        resource = request.payload
        correlation_identifier = request.correlation_identifier
        if 'Users' in request.request.path:
            return self.update_user(request.request, resource, correlation_identifier)

        if 'Groups' in request.request.path:
            return self.update_group(request.request, resource, correlation_identifier)
