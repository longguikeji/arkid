#!/usr/bin/env python3
from scim_server.protocol.patch_operation2_base import PatchOperation2Base
from scim_server.exceptions import ArgumentNullException
from scim_server.protocol.operation_value import OperationValue


class PatchOperation2(PatchOperation2Base):
    Template = "{0}: [{1}]"

    def __init__(self, operation_name, path_expression):
        super().__init__(operation_name, path_expression)
        self.values = []

    def add_value(self, value):
        if not value:
            raise ArgumentNullException(value)
        self.values.append(value)

    @classmethod
    def create(cls, operation_name, path_expression, value):
        if not path_expression:
            raise ArgumentNullException(path_expression)

        if not value:
            raise ArgumentNullException(value)

        operation_value = OperationValue()
        operation_value.value = value

        result = PatchOperation2(operation_name, path_expression)
        result.add_value(operation_value)
        return result

    @property
    def value(self):
        return self.values

    def __str__(self):
        all_values = '\n'.join([str(value) for value in self.values])
        operation = super().__str__()
        result = self.Template.format(operation, all_values)
