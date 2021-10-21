#!/usr/bin/env python3
from scim_server.schemas.typed_item import TypedItem
from scim_server.schemas.attribute_names import AttributeNames


class RoleBase(TypedItem):
    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, value):
        self._display = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @classmethod
    def from_dict(cls, d):
        obj = super().from_dict(d)
        if AttributeNames.Value in d:
            obj.value = d.get(AttributeNames.Value)
        if AttributeNames.Display in d:
            obj.display = d.get(AttributeNames.Display)

        return obj

    def to_dict(self):
        d = super().to_dict()
        if self.value:
            d[AttributeNames.Value] = self.value
        if self.display:
            d[AttributeNames.Display] = self.display
        return d
