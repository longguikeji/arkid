#!/usr/bin/env python3
import json
from scim_server.protocol.patch_operation2_base import PatchOperation2Base
from scim_server.exceptions import ArgumentNullException
from scim_server.protocol.operation_value import OperationValue


class PatchOperation2SingleValued(PatchOperation2Base):
    Template = "{0}: [{1}]"

    def __init__(self, operation_name, path_expression, value):
        super().__init__(operation_name, path_expression)
        if not value:
            raise ArgumentNullException(value)
        self.value = value

    def __str__(self):
        operation = super().__str__()
        result = self.Template.format(operation, self.value)
        return result
