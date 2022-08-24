#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames
from pydantic import BaseModel
from typing import Optional


class Name(BaseModel):
    formatted: Optional[str] = None
    familyName: Optional[str] = None
    givenName: Optional[str] = None
    honorificPrefix: Optional[str] = None
    honorificSuffix: Optional[str] = None

    # @property
    # def formatted(self):
    #     if not hasattr(self, '_formatted'):
    #         return None
    #     return self._formatted

    # @formatted.setter
    # def formatted(self, value):
    #     self._formatted = value

    # @property
    # def family_name(self):
    #     if not hasattr(self, '_family_name'):
    #         return None
    #     return self._family_name

    # @family_name.setter
    # def family_name(self, value):
    #     self._family_name = value

    # @property
    # def given_name(self):
    #     if not hasattr(self, '_given_name'):
    #         return None
    #     return self._given_name

    # @given_name.setter
    # def given_name(self, value):
    #     self._given_name = value

    # @property
    # def honorific_prefix(self):
    #     if not hasattr(self, '_honorific_prefix'):
    #         return None
    #     return self._honorific_prefix

    # @honorific_prefix.setter
    # def honorific_prefix(self, value):
    #     self._honorific_prefix = value

    # @property
    # def honorific_suffix(self):
    #     if not hasattr(self, '_honorific_suffix'):
    #         return None
    #     return self._honorific_suffix

    # @honorific_suffix.setter
    # def honorific_suffix(self, value):
    #     self._honorific_suffix = value

    # @classmethod
    # def from_dict(cls, d):
    #     obj = cls()
    #     if AttributeNames.Formatted in d:
    #         obj.formatted = d.get(AttributeNames.Formatted)
    #     if AttributeNames.FamilyName in d:
    #         obj.family_name = d.get(AttributeNames.FamilyName)
    #     if AttributeNames.GivenName in d:
    #         obj.given_name = d.get(AttributeNames.GivenName)
    #     if AttributeNames.HonorificPrefix in d:
    #         obj.honorific_prefix = d.get(AttributeNames.HonorificPrefix)
    #     if AttributeNames.HonorificSuffix in d:
    #         obj.honorific_suffix = d.get(AttributeNames.HonorificSuffix)

    #     return obj

    # def to_dict(self):
    #     d = {}
    #     if self.formatted is not None:
    #         d[AttributeNames.Formatted] = self.formatted
    #     if self.family_name is not None:
    #         d[AttributeNames.FamilyName] = self.family_name
    #     if self.given_name is not None:
    #         d[AttributeNames.GivenName] = self.given_name
    #     if self.honorific_prefix is not None:
    #         d[AttributeNames.HonorificPrefix] = self.honorific_prefix
    #     if self.honorific_suffix is not None:
    #         d[AttributeNames.HonorificSuffix] = self.honorific_suffix
    #     return d
