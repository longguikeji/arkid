#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames


class TypedItem:
    @property
    def item_type(self):
        if not hasattr(self, '_item_type'):
            return None
        return self._item_type

    @item_type.setter
    def item_type(self, value):
        self._item_type = value

    @property
    def primary(self):
        if not hasattr(self, '_primary'):
            return None
        return self._primary

    @primary.setter
    def primary(self, value):
        self._primary = value

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        if AttributeNames.Type in d:
            obj.type = d.get(AttributeNames.Type)
        if AttributeNames.Primary in d:
            obj.primary = d.get(AttributeNames.Primary)

        return obj

    def to_dict(self):
        d = {}
        if self.item_type is not None:
            d[AttributeNames.Type] = self.item_type
        if self.primary is not None:
            d[AttributeNames.Primary] = self.primary
        return d
