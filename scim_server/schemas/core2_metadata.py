#!/usr/bin/env python3
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class Core2Metadata(BaseModel):
    resourceType: str
    created: Optional[datetime] 
    lastModified: Optional[datetime]
    location: Optional[HttpUrl]
    version: Optional[str]

    # @property
    # def resource_type(self):
    #     if not hasattr(self, '_resource_type'):
    #         return None
    #     return self._resource_type

    # @resource_type.setter
    # def resource_type(self, value):
    #     self._resource_type = value

    # @classmethod
    # def from_dict(cls, d):
    #     obj = cls()
    #     if AttributeNames.ResourceType in d:
    #         obj.resource_type = d.get(AttributeNames.ResourceType)

    #     return obj

    # def to_dict(self):
    #     d = {}
    #     if self.resource_type is not None:
    #         d[AttributeNames.ResourceType] = self.resource_type
    #     return d
