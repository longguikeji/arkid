#!/usr/bin/env python3
from scim_server.schemas.schematized import Schematized
from scim_server.schemas.bulk_requests_feature import BulkRequestsFeature
from scim_server.schemas.filter_feature import FilterFeature
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.schemas.feature import Feature
from scim_server.schemas.authentication_scheme import AuthenticationScheme
from typing import List, Optional
from pydantic import HttpUrl

class ServiceConfigurationBase(Schematized):
    authenticationSchemes: List[AuthenticationScheme]
    # def __init__(self):
    #     super().__init__()
    #     self._authentication_schemes = []
    documentation_resource: Optional[HttpUrl]
    patch: Feature
    bulk: BulkRequestsFeature
    filter: FilterFeature
    changePassword: Feature
    sort: Feature
    etag: Feature

    def add_authentication_scheme(self, authentication_scheme:AuthenticationScheme) -> None:
        if not self.authenticationSchemes:
            self.authenticationSchemes = []
        self.authenticationSchemes.append(authentication_scheme)

    # @property
    # def authentication_schemes(self):
    #     return self._authentication_schemes

    # @property
    # def bulk_requests(self):
    #     return self._bulk_requests

    # @bulk_requests.setter
    # def bulk_requests(self, value):
    #     self._bulk_requests = value

    # @property
    # def documentation_resource(self):
    #     return self._documentation_resource

    # @documentation_resource.setter
    # def documentation_resource(self, value):
    #     self._documentation_resource = value

    # @property
    # def entity_tags(self):
    #     return self._entity_tags

    # @entity_tags.setter
    # def entity_tags(self, value):
    #     self._entity_tags = value

    # @property
    # def filtering(self):
    #     return self._filtering

    # @filtering.setter
    # def filtering(self, value):
    #     self._filtering = value

    # @property
    # def password_change(self):
    #     return self._password_change

    # @password_change.setter
    # def password_change(self, value):
    #     self._password_change = value

    # @property
    # def patching(self):
    #     return self._patching

    # @patching.setter
    # def patching(self, value):
    #     self._patching = value

    # @property
    # def sorting(self):
    #     return self._sorting

    # @sorting.setter
    # def sorting(self, value):
    #     self._sorting = value
