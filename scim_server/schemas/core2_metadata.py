#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames


class Core2Metadata:
    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value):
        self._resource_type = value

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        if AttributeNames.ResourceType in d:
            obj.resource_type = d.get(AttributeNames.ResourceType)

        return obj

    def to_dict(self):
        d = {}
        if self.resource_type:
            d[AttributeNames.ResourceType] = self.resource_type
        return d
