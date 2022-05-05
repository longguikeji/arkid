#!/usr/bin/env python3
from scim_server.schemas.core2_user_base import Core2UserBase
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.extension_attribute_enterprise_user import (
    ExtensionAttributeEnterpriseUser,
)
from scim_server.schemas.attribute_names import AttributeNames
from typing import Optional
from pydantic import Field


class Core2EnterpriseUser(Core2UserBase):

    enterprise_extension: Optional[ExtensionAttributeEnterpriseUser] = Field(
        None, alias=AttributeNames.ExtensionEnterpriseUser2
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_schema(SchemaIdentifiers.Core2EnterpriseUser)
        self.enterprise_extension = ExtensionAttributeEnterpriseUser()

    # @property
    # def enterprise_extension(self):
    #     if not hasattr(self, '_enterprise_extension'):
    #         return None
    #     return self._enterprise_extension

    # @enterprise_extension.setter
    # def enterprise_extension(self, value):
    #     self._enterprise_extension = value

    # @classmethod
    # def from_dict(cls, d):
    #     obj = super().from_dict(d)
    #     if AttributeNames.ExtensionEnterpriseUser2 in d:
    #         extension = ExtensionAttributeEnterpriseUser2.from_dict(
    #             d.get(AttributeNames.ExtensionEnterpriseUser2)
    #         )
    #         obj.enterprise_extension = extension
    #     return obj

    # def to_dict(self):
    #     d = super().to_dict()
    #     if self.enterprise_extension is not None:
    #         d[
    #             AttributeNames.ExtensionEnterpriseUser2
    #         ] = self.enterprise_extension.to_dict()

    #     return d
