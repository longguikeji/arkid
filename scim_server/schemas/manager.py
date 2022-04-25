#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames
from pydantic import BaseModel


class Manager(BaseModel):
    value: str
    display_name: str
    # @classmethod
    # def from_dict(cls, d):
    #     obj = cls()
    #     if AttributeNames.Value in d:
    #         obj.value = d.get(AttributeNames.Value)
    #     if AttributeNames.DisplayName in d:
    #         obj.display_name = d.get(AttributeNames.DisplayName)
    #     return obj

    # def to_dict(self):
    #     result = {}
    #     if self.value is not None:
    #         result[AttributeNames.Value] = self.value
    #     if self.display_name is not None:
    #         result[AttributeNames.DisplayName] = self.display_name
    #     return result

    # @property
    # def value(self):
    #     if not hasattr(self, '_value'):
    #         return None
    #     return self._value

    # @value.setter
    # def value(self, value):
    #     self._value = value

    # @property
    # def display_name(self):
    #     if not hasattr(self, '_display_name'):
    #         return None
    #     return self._display_name

    # @display_name.setter
    # def display_name(self, value):
    #     self._display_name = value
