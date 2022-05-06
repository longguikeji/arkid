#!/usr/bin/env python3
from scim_server.schemas.core2_group_base import GroupBase
from scim_server.schemas.core2_metadata import Core2Metadata
from scim_server.schemas.types import Types
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from typing import Optional


class Core2Group(GroupBase):
    meta: Optional[Core2Metadata]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_schema(SchemaIdentifiers.Core2Group)
        self.meta = Core2Metadata(resourceType=Types.Group)
        # self._custom_extension = {}

    # @property
    # def custom_extension(self):
    #     if not hasattr(self, '_custom_extension'):
    #         return None
    #     return self._custom_extension

    # def add_custom_attribute(self, key, value):
    #     if (
    #         key
    #         and key.startswith(SchemaIdentifiers.PrefixExtension)
    #         and type(value) == dict
    #     ):
    #         self._custom_extension[key] = value

    # def to_dict(self):
    #     result = super().to_dict()
    #     for key, value in self.custom_extension.items():
    #         result[key] = value
    #     return result

    # # TODO custom extension
    # @classmethod
    # def from_dict(cls, d):
    #     return super().from_dict(d)
