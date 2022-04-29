#!/usr/bin/env python3

from scim_server.schemas.user_base import UserBase
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.core2_metadata import Core2Metadata
from scim_server.schemas.types import Types
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.address import Address
from scim_server.schemas.electronic_mail_address import ElectroicMailAddress
from scim_server.schemas.instant_messaging import InstantMessaging
from scim_server.schemas.name import Name
from scim_server.schemas.phone_number import PhoneNumber
from scim_server.schemas.role import Role
from typing import List


class Core2UserBase(UserBase):
    metadata: Core2Metadata
    active: bool
    address: List[Address]
    display_name: str
    electronic_mail_addresses: ElectroicMailAddress
    instant_messagings: InstantMessaging
    locale: str
    metadate: dict
    name: str
    nickname: str
    phone_numbers: List[PhoneNumber]
    preferred_language: str
    roles: List[Role]
    timezone: str
    title: str
    user_type: str
    # def __init__(self):
    #     super().__init__()
    #     self.add_schema(SchemaIdentifiers.Core2User)
    #     self.metadata = Core2Metadata()
    #     self.metadata.resource_type = Types.User
    #     self._custom_extension = {}

    # @property
    # def active(self):
    #     if not hasattr(self, '_active'):
    #         return None
    #     return self._active

    # @active.setter
    # def active(self, value):
    #     self._active = value

    # @property
    # def addresses(self):
    #     if not hasattr(self, '_addresses'):
    #         return None
    #     return self._addresses

    # @addresses.setter
    # def addresses(self, value):
    #     self._addresses = value

    @property
    def custom_extension(self):
        if not hasattr(self, '_custom_extension'):
            return None
        return self._custom_extension

    # @property
    # def display_name(self):
    #     if not hasattr(self, '_display_name'):
    #         return None
    #     return self._display_name

    # @display_name.setter
    # def display_name(self, value):
    #     self._display_name = value

    # @property
    # def electronic_mail_addresses(self):
    #     if not hasattr(self, '_electronic_mail_addresses'):
    #         return None
    #     return self._electronic_mail_addresses

    # @electronic_mail_addresses.setter
    # def electronic_mail_addresses(self, value):
    #     self._electronic_mail_addresses = value

    # @property
    # def instant_messagings(self):
    #     if not hasattr(self, '_instant_messagings'):
    #         return None
    #     return self._instant_messagings

    # @instant_messagings.setter
    # def instant_messagings(self, value):
    #     self._instant_messagings = value

    # @property
    # def locale(self):
    #     if not hasattr(self, '_locale'):
    #         return None
    #     return self._locale

    # @locale.setter
    # def locale(self, value):
    #     self._locale = value

    # @property
    # def metadata(self):
    #     if not hasattr(self, '_metadata'):
    #         return None
    #     return self._metadata

    # @metadata.setter
    # def metadata(self, value):
    #     self._metadata = value

    # @property
    # def name(self):
    #     if not hasattr(self, '_name'):
    #         return None
    #     return self._name

    # @name.setter
    # def name(self, value):
    #     self._name = value

    # @property
    # def nickname(self):
    #     if not hasattr(self, '_nickname'):
    #         return None
    #     return self._nickname

    # @nickname.setter
    # def nickname(self, value):
    #     self._nickname = value

    # @property
    # def phone_numbers(self):
    #     if not hasattr(self, '_phone_numbers'):
    #         return None
    #     return self._phone_numbers

    # @phone_numbers.setter
    # def phone_numbers(self, value):
    #     self._phone_numbers = value

    # @property
    # def preferred_language(self):
    #     if not hasattr(self, '_preferred_language'):
    #         return None
    #     return self._preferred_language

    # @preferred_language.setter
    # def preferred_language(self, value):
    #     self._preferred_language = value

    # @property
    # def roles(self):
    #     if not hasattr(self, '_roles'):
    #         return None
    #     return self._roles

    # @roles.setter
    # def roles(self, value):
    #     self._roles = value

    # @property
    # def time_zone(self):
    #     if not hasattr(self, '_time_zone'):
    #         return None
    #     return self._time_zone

    # @time_zone.setter
    # def time_zone(self, value):
    #     self._time_zone = value

    # @property
    # def title(self):
    #     if not hasattr(self, '_title'):
    #         return None
    #     return self._title

    # @title.setter
    # def title(self, value):
    #     self._title = value

    # @property
    # def user_type(self):
    #     if not hasattr(self, '_user_type'):
    #         return None
    #     return self._user_type

    # @user_type.setter
    # def user_type(self, value):
    #     self._user_type = value

    # def add_custom_attribute(self, key, value):
    #     if (
    #         key
    #         and key.startswith(SchemaIdentifiers.PrefixExtension)
    #         and not key.startswith(SchemaIdentifiers.Core2EnterpriseUser)
    #         and type(value) == dict
    #     ):
    #         self._custom_extension[key] = value

    # def to_dict(self):
    #     result = super().to_dict()
    #     for key, value in self.custom_extension.items():
    #         result[key] = value
    #     simple_field_map = {
    #         'active': AttributeNames.Active,
    #         'display_name': AttributeNames.DisplayName,
    #         'locale': AttributeNames.Locale,
    #         'nickname': AttributeNames.Nickname,
    #         'preferred_language': AttributeNames.PreferredLanguage,
    #         'time_zone': AttributeNames.TimeZone,
    #         'title': AttributeNames.Title,
    #         'user_type': AttributeNames.UserType,
    #     }
    #     for key, value in simple_field_map.items():
    #         if getattr(self, key):
    #             result[value] = getattr(self, key)

    #     if self.addresses is not None:
    #         result[AttributeNames.Addresses] = [
    #             item.to_dict() for item in self.addresses
    #         ]
    #     if self.electronic_mail_addresses is not None:
    #         result[AttributeNames.ElectronicMailAddresses] = [
    #             item.to_dict() for item in self.electronic_mail_addresses
    #         ]
    #     if self.instant_messagings is not None:
    #         result[AttributeNames.Ims] = [
    #             item.to_dict() for item in self.instant_messagings
    #         ]
    #     if self.metadata is not None:
    #         result[AttributeNames.Metadata] = self.metadata.to_dict()

    #     if self.name is not None:
    #         result[AttributeNames.Name] = self.name.to_dict()

    #     if self.phone_numbers is not None:
    #         result[AttributeNames.PhoneNumbers] = [
    #             item.to_dict() for item in self.phone_numbers
    #         ]

    #     if self.roles is not None:
    #         result[AttributeNames.Roles] = [item.to_dict() for item in self.roles]

    #     return result

    # # TODO custom extension
    # @classmethod
    # def from_dict(cls, d):
    #     obj = super().from_dict(d)
    #     simple_field_map = {
    #         AttributeNames.Active: 'active',
    #         AttributeNames.DisplayName: 'display_name',
    #         AttributeNames.Locale: 'locale',
    #         AttributeNames.Nickname: 'nick_name',
    #         AttributeNames.PreferredLanguage: 'preferred_language',
    #         AttributeNames.TimeZone: 'time_zone',
    #         AttributeNames.Title: 'title',
    #         AttributeNames.UserType: 'user_type',
    #     }
    #     for key, value in simple_field_map.items():
    #         if key in d:
    #             setattr(obj, value, d.get(key))
    #     if AttributeNames.Addresses in d:
    #         obj.addresses = [
    #             Address.from_dict(item) for item in d.get(AttributeNames.Addresses)
    #         ]
    #     if AttributeNames.ElectronicMailAddresses in d:
    #         obj.electronic_mail_addresses = [
    #             ElectroicMailAddress.from_dict(item)
    #             for item in d.get(AttributeNames.ElectronicMailAddresses)
    #         ]
    #     if AttributeNames.Ims in d:
    #         obj.instant_messagings = [
    #             InstantMessaging.from_dict(item) for item in d.get(AttributeNames.Ims)
    #         ]

    #     if AttributeNames.Metadata in d:
    #         obj.metadata = Core2Metadata.from_dict(d.get(AttributeNames.Metadata))
    #     if AttributeNames.Name in d:
    #         obj.name = Name.from_dict(d.get(AttributeNames.Name))
    #     if AttributeNames.PhoneNumbers in d:
    #         obj.phone_numbers = [
    #             PhoneNumber.from_dict(item)
    #             for item in d.get(AttributeNames.PhoneNumbers)
    #         ]
    #     if AttributeNames.Roles in d:
    #         obj.roles = [Role.from_dict(item) for item in d.get(AttributeNames.Roles)]
    #     return obj
