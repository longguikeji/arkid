#!/usr/bin/env python3
from scim_server.protocol.retrieval_parameters import RetrievalParameters
from scim_server.protocol.schema_identifier import SchemaIdentifier
from scim_server.protocol.query import Query


class QueryParameters(RetrievalParameters):
    def __init__(
        self,
        schema_identifier,
        path,
        filters,
        requested_attribute_paths,
        excluded_attribute_paths,
    ):
        if not path:
            path = SchemaIdentifier(schema_identifier).find_path()
        super().__init__(
            schema_identifier, path, requested_attribute_paths, excluded_attribute_paths
        )
        if not filters:
            self.alternate_filters = []
        else:
            self.alternate_filters = filters

    def __str__(self):
        query = Query()
        query.alternate_filters = self.alternate_filters
        query.requested_attribute_paths = self.requested_attribute_paths
        query.excluded_attribute_paths = self.excluded_attribute_paths
        query.pagination_parameters = self.pagination_parameters
        result = query.compose()
        return result
