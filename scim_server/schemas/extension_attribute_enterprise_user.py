#!/usr/bin/env python3

from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.manager import Manager
from typing import Optional
from pydantic import BaseModel

class ExtensionAttributeEnterpriseUser(BaseModel):
    employeeNumber: Optional[str]
    costCenter: Optional[str]
    organization: Optional[str]
    division: Optional[str]
    department: Optional[str]
    manager: Optional[Manager]
    # @classmethod
    # def from_dict(cls, d):
    #     obj = super().from_dict(d)
    #     if AttributeNames.Manager in d:
    #         manager = Manager.from_dict(d.get(AttributeNames.Manager))
    #         obj.manager = manager
    #     return obj

    # def to_dict(self):
    #     d = super().to_dict()
    #     if self.manager is not None:
    #         d[AttributeNames.Manager] = self.manager.to_dict()

    #     return d

    # @property
    # def manager(self):
    #     if not hasattr(self, '_manager'):
    #         return None
    #     return self._manager

    # @manager.setter
    # def manager(self, value):
    #     self._manager = value
