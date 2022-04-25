#!/usr/bin/env python3
import json
from scim_server.protocol.patch_operation2_base import PatchOperation2Base
from scim_server.exceptions import ArgumentNullException
from scim_server.protocol.operation_value import OperationValue


class PatchOperation2Combined(PatchOperation2Base):
    Template = "{0}: [{1}]"

    def __init__(self, operation_name, path_expression):
        super().__init__(operation_name, path_expression)
        self.values = None

    @classmethod
    def create(cls, operation_name, path_expression, value):
        if not path_expression:
            raise ArgumentNullException(path_expression)

        if not value:
            raise ArgumentNullException(value)

        operation_value = OperationValue()
        operation_value.value = value

        result = cls(operation_name, path_expression)
        result.value = operation_value
        return result

    @property
    def value(self):
        if not value:
            return None
        result = json.dumps(self.values)
        return result

    @value.setter
    def value(self, value):
        self.values = value

    @classmethod
    def from_dict(cls, d):
        pass

    def __str__(self):
        all_values = self.value
        operation = super().__str__()
        result = self.Template.format(operation, all_values)
        return result
