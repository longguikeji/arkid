#!/usr/bin/env python3
from scim_server.schemas.resource import Resource
from scim_server.schemas.attribute_names import AttributeNames


class UserBase(Resource):
    def __init__(self):
        super().__init__()

    @property
    def user_name(self):
        if not hasattr(self, '_user_name'):
            return None
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value

    def to_dict(self):
        result = super().to_dict()
        if self.user_name:
            result[AttributeNames.UserName] = self.user_name
        return result

    @classmethod
    def from_dict(cls, d):
        obj = super().from_dict(d)
        if AttributeNames.UserName in d:
            obj.user_name = d.get(AttributeNames.UserName)
        return obj
