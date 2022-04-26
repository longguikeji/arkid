#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue
from scim_server.schemas.attribute_names import AttributeNames
from typing import Optional

class Role(TypedValue):
    display: Optional[str]
    # @property
    # def display(self):
    #     if not hasattr(self, '_display'):
    #         return None
    #     return self._display

    # @display.setter
    # def display(self, value):
    #     self._display = value

    # @property
    # def value(self):
    #     if not hasattr(self, '_value'):
    #         return None
    #     return self._value

    # @value.setter
    # def value(self, value):
    #     self._value = value

    # @classmethod
    # def from_dict(cls, d):
    #     obj = super().from_dict(d)
    #     if AttributeNames.Value in d:
    #         obj.value = d.get(AttributeNames.Value)
    #     if AttributeNames.Display in d:
    #         obj.display = d.get(AttributeNames.Display)

    #     return obj

    # def to_dict(self):
    #     d = super().to_dict()
    #     if self.value is not None:
    #         d[AttributeNames.Value] = self.value
    #     if self.display is not None:
    #         d[AttributeNames.Display] = self.display
    #     return d
