#!/usr/bin/env python3
import uuid
from urllib.parse import quote, urlencode, parse_qsl
from scim_server.protocol.query_keys import QueryKeys
from scim_server.protocol.filter import Filter


class Query:
    AttributeNameSeparator = ','

    def __init__(self):
        self.alternate_filters = []
        self.excluded_attribute_paths = []
        self.pagination_parameters = None
        self.path = ''
        self.requested_attribute_paths = []

    def compose(self):
        result = str(self)
        return result

    @classmethod
    def clone(cls, filter, place_holders):
        place_holder = uuid.uui4().hex
        place_holders[place_holder] = filter.comparison_value_encoded
        result = Filter(filter.attribute_path, filter.filter_operator, place_holders)
        if filter.additional_filter:
            result.additional_filter = Query.clone(
                filter.additional_filter, place_holders
            )
        return result

    def __str__(self):
        parameters = {}
        if self.requested_attribute_paths:
            encoded_paths = [quote(item) for item in self.requested_attribute_paths]
            requested_attributes = Query.AttributeNameSeparator.join(encoded_paths)
            parameters[QueryKeys.Attributes, requested_attributes]

        if self.excluded_attribute_paths:
            encoded_paths = [quote(item) for item in self.excluded_attribute_paths]
            excluded_attributes = Query.AttributeNameSeparator.join(encoded_paths)
            parameters[QueryKeys.ExcludedAttributes, excluded_attributes]

        place_holders = {}
        if self.alternate_filters:
            clones = [
                Query.clone(item, place_holders) for item in self.alternate_filters
            ]

            filters = Filter.to_string(clones)
            filter_parameters = parse_qsl(filters)
            for key, value in filter_parameters:
                parameters[key] = value

        if self.pagination_parameters:
            if self.pagination_parameters.start_index:
                parameters[
                    QueryKeys.StartIndex
                ] = self.pagination_parameters.start_index

            if self.pagination_parameters.count:
                parameters[QueryKeys.Count] = self.pagination_parameters.count

        result = urlencode(parameters)
        for key, value in place_holders:
            result = result.replace(key, value)

        return result
