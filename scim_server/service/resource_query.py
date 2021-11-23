#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException, NotAcceptableException
from scim_server.protocol.query_keys import QueryKeys
from scim_server.protocol.pagination_parameters import PaginationParameters
from scim_server.protocol.filter import Filter


class ResourceQuery:
    SeperatorAttributes = ','

    def __init__(self):
        self.filters = []
        self.attributes = []
        self.excluded_attributes = []
        self.pagination_parameters = None

    @classmethod
    def create(cls, filters, attributes, excluded_attributes):
        if filters is None:
            raise ArgumentNullException('filters')
        if attributes is None:
            raise ArgumentNullException('attributes')
        if excluded_attributes is None:
            raise ArgumentNullException('excluded_attributes')

        return cls(filters, attributes, excluded_attributes)

    @classmethod
    def initialize(cls, request):
        if not request:
            raise ArgumentNullException('request')

        obj = cls()
        query_dict = request.GET.dict()
        for key, value in query_dict.items():
            if key == QueryKeys.Attributes:
                if value:
                    obj.attributes = ResourceQuery.parse_attribute(value)

            if key == QueryKeys.ExcludedAttributes:
                if value:
                    obj.excluded_attributes = ResourceQuery.parse_attribute(value)

            if key == QueryKeys.Count:

                def set_pagination_count(pagination, count):
                    pagination.count = count

                obj.apply_pagination_parameter(value, set_pagination_count)

            if key == QueryKeys.StartIndex:

                def set_pagination_start_index(pagination, start_index):
                    pagination.start_index = start_index

                obj.apply_pagination_parameter(value, set_pagination_start_index)

            if key == QueryKeys.Filter:
                if value:
                    obj.filters = ResourceQuery.parse_filters(value)
        return obj

    def apply_pagination_parameter(self, value, action):
        if not action:
            raise ArgumentNullException('action')
        if not value:
            return

        parsed_value = int(value)
        if not self.pagination_parameters:
            self.pagination_parameters = PaginationParameters()
        action(self.pagination_parameters, parsed_value)

    @classmethod
    def parse_attributes(cls, attributes_expression):
        if not attributes_expression:
            raise ArgumentNullException('attributes_expression')
        return attributes_expression.split(cls.SeperatorAttributes)

    @classmethod
    def parse_filters(cls, filter_expression):
        if not filter_expression:
            raise ArgumentNullException('filter_expression')
        results = Filter.try_parse(filter_expression)
        if not results:
            raise NotAcceptableException(filter_expression)
        return results
