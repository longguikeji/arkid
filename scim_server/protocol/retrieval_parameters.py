#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException
from scim_server.protocol.query import Query


class RetrievalParameters:
    def __init__(
        self,
        schema_identifier,
        path,
        requested_attribute_paths=[],
        excluded_attribute_paths=[],
    ):

        if not schema_identifier:
            raise ArgumentNullException('schema_identifier')

        if not path:
            raise ArgumentNullException('path')

        if requested_attribute_paths is None:
            requested_attribute_paths = []

        if excluded_attribute_paths is None:
            requested_attribute_paths = []

        self.schema_identifier = schema_identifier
        self.path = path
        self.requested_attribute_paths = requested_attribute_paths
        self.excluded_attribute_paths = excluded_attribute_paths

    def __str__(self):
        query = Query()
        query.requested_attribute_paths = self.requested_attribute_paths
        query.excluded_attribute_paths = self.excluded_attribute_paths
        result = query.compose()
        return result
