#!/usr/bin/env python3


class OperationValue:
    Template = "{0} {1}"

    def __init__(self, reference='', value=''):
        self.reference = reference
        self.value = value

    def __str__(self):
        return self.Template.format(self.value, self.reference).strip()
