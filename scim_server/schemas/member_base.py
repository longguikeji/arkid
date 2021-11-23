#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames


class MemberBase:
    @property
    def display(self):
        if not hasattr(self, '_display'):
            return None
        return self._display

    @display.setter
    def display(self, value):
        self._display = value

    @property
    def value(self):
        if not hasattr(self, '_value'):
            return None
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def to_dict(self):
        result = {}
        if self.display is not None:
            result[AttributeNames.Display] = self.display

        if self.value is not None:
            result[AttributeNames.Value] = self.value
        return result

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        if AttributeNames.Display in d:
            obj.display = d.get(AttributeNames.Display)
        if AttributeNames.Value in d:
            obj.value = d.get(AttributeNames.Value)
        return obj
