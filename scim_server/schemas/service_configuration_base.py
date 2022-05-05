#!/usr/bin/env python3
from scim_server.schemas.schematized import Schematized
from scim_server.exceptions import ArgumentNullException, ArgumentException


class ServiceConfigurationBase(Schematized):
    def __init__(self):
        super().__init__()
        self._authentication_schemes = []

    def add_authentication_scheme(self, authentication_scheme):
        if not authentication_scheme:
            raise ArgumentNullException('authentication_scheme')
        if not authentication_scheme.name:
            raise ArgumentException('Unnamed Authentication Scheme')
        self._authentication_schemes.append(authentication_scheme)

    @property
    def authentication_schemes(self):
        return self._authentication_schemes

    @property
    def bulk_requests(self):
        return self._bulk_requests

    @bulk_requests.setter
    def bulk_requests(self, value):
        self._bulk_requests = value

    @property
    def documentation_resource(self):
        return self._documentation_resource

    @documentation_resource.setter
    def documentation_resource(self, value):
        self._documentation_resource = value

    @property
    def entity_tags(self):
        return self._entity_tags

    @entity_tags.setter
    def entity_tags(self, value):
        self._entity_tags = value

    @property
    def filtering(self):
        return self._filtering

    @filtering.setter
    def filtering(self, value):
        self._filtering = value

    @property
    def password_change(self):
        return self._password_change

    @password_change.setter
    def password_change(self, value):
        self._password_change = value

    @property
    def patching(self):
        return self._patching

    @patching.setter
    def patching(self, value):
        self._patching = value

    @property
    def sorting(self):
        return self._sorting

    @sorting.setter
    def sorting(self, value):
        self._sorting = value
