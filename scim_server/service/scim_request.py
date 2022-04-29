#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.schemas.schema_constants import SchemaConstants


class ScimRequest:
    def __init__(self, request, payload, correlation_identifier, extensions):
        if not request:
            raise ArgumentNullException
        if not correlation_identifier:
            raise ArgumentNullException
        if not payload:
            raise ArgumentNullException

        self.base_resource_identifier = ScimRequest.get_base_resource_identifier(
            request
        )
        self.request = request
        self.payload = payload
        self.correlation_identifier = correlation_identifier
        self.extensions = extensions

    @property
    def base_resource_identifier(self):
        return self._base_resource_identifier

    @base_resource_identifier.setter
    def base_resource_identifier(self, value):
        self._base_resource_identifier = value

    @property
    def correlation_identifier(self):
        return self._correlation_identifier

    @correlation_identifier.setter
    def correlation_identifier(self, value):
        self._correlation_identifier = value

    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, value):
        self._extensions = value

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value):
        self._request = value

    @classmethod
    def get_base_resource_identifier(cls, request):
        segment_separator = '/'
        segment_interface = (
            segment_separator + SchemaConstants.PathInterface + segment_separator
        )

        last_segment = request.path.split(segment_separator)[-1]
        if last_segment == SchemaConstants.PathInterface:
            return request.build_absolute_uri()
        resource_identifier = request.build_absolute_uri()
        index_interface = resource_identifier.rfind(segment_interface)
        if index_interface < 0:
            raise ArgumentException('invalid request')

        base_resource = resource_identifier[0:index_interface]
        return base_resource
