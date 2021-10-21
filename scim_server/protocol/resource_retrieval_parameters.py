#!/usr/bin/env python3
from scim_server.protocol.retrieval_parameters import RetrievalParameters
from scim_server.protocol.resource_identifier import ResourceIdentifier
from scim_server.exceptions import ArgumentNullException


class ResourceRetrievalParamters(RetrievalParameters):
    def __init__(
        self,
        schema_identifier,
        path,
        resource_identifier,
        requested_attribute_paths,
        excluded_attribute_paths,
    ):
        super().__init__(
            schema_identifier, path, requested_attribute_paths, excluded_attribute_paths
        )

        if not resource_identifier:
            raise ArgumentNullException('resource_identifier')

        self.resource_identifier = ResourceIdentifier(
            schema_identifier, resource_identifier
        )
        self.identifier = resource_identifier
