#!/usr/bin/env python3
from scim_server.schemas.resource import Resource
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.member import Member
from typing import List


class GroupBase(Resource):
    displayName: str
    members: List[Member] = []
    # @property
    # def display_name(self):
    #     if not hasattr(self, '_display_name'):
    #         return None
    #     return self._display_name

    # @display_name.setter
    # def display_name(self, value):
    #     self._display_name = value

    # @property
    # def members(self):
    #     if not hasattr(self, '_members'):
    #         return None
    #     return self._members

    # @members.setter
    # def members(self, value):
    #     self._members = value

    # def to_dict(self):
    #     result = super().to_dict()
    #     if self.display_name is not None:
    #         result[AttributeNames.DisplayName] = self.display_name

    #     if self.members is not None:
    #         result[AttributeNames.Members] = [item.to_dict() for item in self.members]
    #     return result

    # @classmethod
    # def from_dict(cls, d):
    #     obj = super().from_dict(d)
    #     if AttributeNames.DisplayName in d:
    #         obj.display_name = d.get(AttributeNames.DisplayName)
    #     if AttributeNames.Members in d:
    #         obj.members = [
    #             Member.from_dict(item) for item in d.get(AttributeNames.Members)
    #         ]
    #     return obj
