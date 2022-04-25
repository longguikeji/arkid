#!/usr/bin/env python3
from scim_server.schemas.feature_base import FeatureBase


class BulkRequestsFeature(FeatureBase):
    @classmethod
    def create_unsupported_feature(cls):
        result = BulkRequestsFeature()
        result.supported = False
        return result

    @property
    def concurrent_operations(self):
        return self._concurrent_operations

    @concurrent_operations.setter
    def concurrent_operation(self, value):
        self._concurrent_operations = value

    @property
    def maximum_operations(self):
        return self._maximum_operations

    @maximum_operations.setter
    def maximum_operations(self, value):
        self._maximum_operations = value

    @property
    def maximum_payload_size(self):
        return self._maximum_payload_size

    @maximum_payload_size.setter
    def maximum_payload_size(self, value):
        self._maximum_payload_size = value
