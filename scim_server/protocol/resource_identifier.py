#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException


class ResourceIdentifier:
    def __init__(self, schema_identifier, resource_identifier):
        if not schema_identifier:
            raise ArgumentNullException('schema_identifier')
        if not resource_identifier:
            raise ArgumentNullException('resource_identifier')

        self.schema_identifier = schema_identifier
        self.identifier = resource_identifier

    def __str__(self):
        return "{}/{}".format(self.schema_identifier, self.resource_identifier)
