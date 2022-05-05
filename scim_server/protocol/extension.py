#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException
from pydantic import BaseModel


class Extension:
    def __init__(
        self, schema_identifier, type_name, path, controller, json_deserializing_factory
    ):
        if not schema_identifier:
            raise ArgumentNullException('schema_identifier')

        if not type_name:
            raise ArgumentNullException('type_name')

        if not path:
            raise ArgumentNullException('path')

        if not controller:
            raise ArgumentNullException('controller')

        if not json_deserializing_factory:
            raise ArgumentNullException('json_deserializing_factory')

        self.schema_identifier = schema_identifier
        self.type_name = type_name
        self.path = path
        self.controller = controller
        self.json_deserializing_factory = json_deserializing_factory
