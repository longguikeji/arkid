#!/usr/bin/env python3
from scim_server.schemas.schematized import Schematized
from scim_server.protocol.protocol_schema_identifiers import ProtocolSchemaIdentifiers


class PatchRequest2Base(Schematized):
    def __init__(self, operations=None):
        self.add_schema(ProtocolSchemaIdentifiers.Version2PatchOperation)
        if operations:
            self.operations = operations
        else:
            self.operations = []

    def add_operation(self, operation):
        self.operations.add(operation)

    @classmethod
    def from_dict(cls, json):
        pass
