#!/usr/bin/env python3
import json
from scim_server.exceptions import ArgumentNullException
from scim_server.schemas.attribute_names import AttributeNames


class Schematized:
    def __init__(self):
        self._schemas = []

    def add_schema(self, schema_identifier):
        if schema_identifier not in self._schemas:
            self._schemas.append(schema_identifier)

    def is_schema(self, schema):
        if not schema:
            raise ArgumentNullException('schema')

        for item in self.schemas:
            if item == schema:
                return True
        return False

    @property
    def schemas(self):
        if not hasattr(self, '_schemas'):
            return None
        return self._schemas

    def to_dict(self):
        result = {}
        if self.schemas is not None:
            result[AttributeNames.Schemas] = self.schemas
        return result

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        if AttributeNames.Schemas in d:
            obj._schemas = d.get(AttributeNames.Schemas)
        return obj

    def try_get_path(self):
        return ''

    def try_get_schema_identifier(self):
        return ''
