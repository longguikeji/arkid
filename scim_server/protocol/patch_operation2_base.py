#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException, NotSupportedException
from scim_server.protocol.operation_name import OperationName
from scim_server.protocol.path import Path


class PatchOperation2Base:
    Template = "{0} {1}"

    def __init__(self, name, path_expression):
        if not path_expression:
            raise ArgumentNullException(path_expression)
        self.name = name
        self.path = Path.create(path_expression)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._operation_name = value.name

    @property
    def operation_name(self):
        return self._operation_name

    @operation_name.setter
    def operation_name(self, value):
        enum_values = [item.lower() for item in OperationName.__members__.keys()]
        if value not in enum_values:
            raise NotSupportedException(value)
        self._operation_name = value

    @property
    def path(self):
        if self._path and self.path_expression:
            self._path = Path.create(self.path_expression)
        return self._path

    @path.setter
    def path(self, value):
        self.path_expression = str(value)
        self._path = value

    def __str__(self):
        return self.Template.format(self.operation_name, self.path_expression)
