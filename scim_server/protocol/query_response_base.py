#!/usr/bin/env python3
from scim_server.schemas.schematized import Schematized
from scim_server.exceptions import ArgumentNullException
from scim_server.protocol.protocol_schema_identifiers import ProtocolSchemaIdentifiers
from scim_server.protocol.protocol_attribute_names import ProtocolAttributeNames
from typing import List, Any

class QueryResponseBase(Schematized):
    resources:List[Any] = []
    items_per_page:int = 0
    start_index: int = 0
    total_results: int = 0

    def __init__(self, resources):
        super().__init__()
        if resources is None:
            raise ArgumentNullException('resources')
        self.resources = resources
        self.add_schema(ProtocolSchemaIdentifiers.Version2ListResponse)

    # @property
    # def items_per_page(self):
    #     if not hasattr(self, '_items_per_page'):
    #         return None
    #     return self._items_per_page

    # @items_per_page.setter
    # def items_per_page(self, value):
    #     self._items_per_page = value

    # @property
    # def resources(self):
    #     if not hasattr(self, '_resources'):
    #         return None
    #     return self._resources

    # @resources.setter
    # def resources(self, value):
    #     if value is None:
    #         raise ArgumentNullException('invalid value')
    #     self._resources = value

    # @property
    # def start_index(self):
    #     if not hasattr(self, '_start_index'):
    #         return None
    #     return self._start_index

    # @start_index.setter
    # def start_index(self, value):
    #     self._start_index = value

    # @property
    # def total_results(self):
    #     if not hasattr(self, '_total_results'):
    #         return None
    #     return self._total_results

    # @total_results.setter
    # def total_results(self, value):
    #     self._total_results = value

    # def to_dict(self):
    #     d = super().to_dict()
    #     if self.total_results is not None:
    #         d[ProtocolAttributeNames.TotalResults] = self.total_results

    #     if self.items_per_page is not None:
    #         d[ProtocolAttributeNames.ItemsPerPage] = self.items_per_page

    #     if self.start_index is not None:
    #         d[ProtocolAttributeNames.StartIndex] = self.start_index

    #     if self.resources is not None:
    #         d[ProtocolAttributeNames.Resources] = [
    #             item.to_dict() for item in self.resources
    #         ]
    #     return d
