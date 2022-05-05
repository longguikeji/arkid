#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException, NotSupportedException
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.protocol.protocol_constants import ProtocolConstants
from scim_server.schemas.schema_constants import SchemaConstants


class SchemaIdentifier:
    def __init__(self, value):
        if not value:
            raise ArgumentNullException('value')
        self.value = value

    def find_path(self):
        result = self.try_find_path()
        if not result:
            raise NotSupportedException(self.value)
        return result

    def try_find_path(self):
        path = None
        if self.value in [
            SchemaIdentifiers.Core2EnterpriseUser,
            SchemaIdentifiers.Core2User,
        ]:
            path = ProtocolConstants.PathUsers
        elif self.value == SchemaIdentifiers.Core2Group:
            path = ProtocolConstants.PathGroups
        elif self.value == SchemaIdentifier.NULL:
            path = SchemaConstants.PathInterface
        return path
