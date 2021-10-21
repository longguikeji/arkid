#!/usr/bin/env python3
from scim_server.schemas.typed_item import TypedItem
from scim_server.schemas.attribute_names import AttributeNames


class AddressBase(TypedItem):
    Home = 'home'
    Other = 'other'
    Untyped = 'untyped'
    Work = 'work'

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, value):
        self._country = value

    @property
    def formatted(self):
        return self._formatted

    @formatted.setter
    def formatted(self, value):
        self._formatted = value

    @property
    def locality(self):
        return self._locality

    @locality.setter
    def locality(self, value):
        self._locality = value

    @property
    def postal_code(self):
        return self._postal_code

    @postal_code.setter
    def postal_code(self, value):
        self._postal_code = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def street_address(self):
        return self._street_address

    @street_address.setter
    def street_address(self, value):
        self._street_address = value

    @classmethod
    def from_dict(cls, d):
        obj = super().from_dict(d)
        if AttributeNames.Country in d:
            obj.country = d.get(AttributeNames.Country)
        if AttributeNames.Formatted in d:
            obj.formatted = d.get(AttributeNames.Formatted)
        if AttributeNames.Locality in d:
            obj.locality = d.get(AttributeNames.Locality)
        if AttributeNames.PostalCode in d:
            obj.postal_code = d.get(AttributeNames.PostalCode)
        if AttributeNames.Region in d:
            obj.region = d.get(AttributeNames.Region)
        if AttributeNames.StreetAddress in d:
            obj.street_address = d.get(AttributeNames.StreetAddress)

        return obj

    def to_dict(self):
        d = super().to_dict()
        if self.country:
            d[AttributeNames.Country] = self.country
        if self.formatted:
            d[AttributeNames.Formatted] = self.formatted
        if self.locality:
            d[AttributeNames.Locality] = self.locality
        if self.postal_code:
            d[AttributeNames.PostalCode] = self.postal_code
        if self.region:
            d[AttributeNames.Region] = self.region
        if self.street_address:
            d[AttributeNames.StreetAddress] = self.street_address
        return d
