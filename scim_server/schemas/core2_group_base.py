#!/usr/bin/env python3
from scim_server.schemas.group_base import GroupBase
from scim_server.schemas.core2_metadata import Core2Metadata
from scim_server.schemas.types import Types
from scim_server.schemas.schema_identifiers import SchemaIdentifiers


class Core2GroupBase(GroupBase):
    def __init__(self):
        super().__init__()
        self.add_schema(SchemaIdentifiers.Core2Group)
        self.metadata = Core2Metadata()
        self.metadata.resouce_type = Types.Group
        self._custom_extension = {}

    @property
    def custom_extension(self):
        if not hasattr(self, '_custom_extension'):
            return None
        return self._custom_extension

    def add_custom_attribute(self, key, value):
        if (
            key
            and key.startswith(SchemaIdentifiers.PrefixExtension)
            and type(value) == dict
        ):
            self._custom_extension[key] = value

    def to_dict(self):
        result = super().to_dict()
        for key, value in self.custom_extension.items():
            result[key] = value
        return result

    # TODO custom extension
    @classmethod
    def from_dict(cls, d):
        return super().from_dict(d)
