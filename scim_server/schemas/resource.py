#!/usr/bin/env python3
from scim_server.schemas.schematized import Schematized
from scim_server.schemas.attribute_names import AttributeNames


class Resource(Schematized):
    def __init__(self):
        super().__init__()

    @property
    def external_identifier(self):
        if not hasattr(self, '_external_identifier'):
            return None
        return self._external_identifier

    @external_identifier.setter
    def external_identifier(self, value):
        self._external_identifier = value

    @property
    def identifier(self):
        if not hasattr(self, '_identifier'):
            return None
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    def try_get_identifier(self, base_identifier):
        return ''

    def try_get_path_identifier(self):
        return ''

    def to_dict(self):
        result = super().to_dict()
        if self.identifier:
            result[AttributeNames.Identifier] = self.identifier

        if self.external_identifier:
            result[AttributeNames.ExternalIdentifier] = self.external_identifier
        return result

    @classmethod
    def from_dict(cls, d):
        obj = super().from_dict(d)
        if AttributeNames.Identifier in d:
            obj.identifier = d.get(AttributeNames.Identifier)
        if AttributeNames.ExternalIdentifier in d:
            obj.external_identifier = d.get(AttributeNames.ExternalIdentifier)
        return obj
