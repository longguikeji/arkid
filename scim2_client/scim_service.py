#!/usr/bin/env python3
import requests
from urllib.parse import urljoin
from .constants import (
    MEDIA_TYPE_SCIM,
    SERVICE_PROVIDER_CONFIG_ENDPOINT,
    RESOURCE_TYPES_ENDPOINT,
    SCHEMAS_ENDPOINT,
)
from .requests import CreateRequestBuilder
from .requests import DeleteRequestBuilder
from .requests import ModifyRequestBuilder
from .requests import ReplaceRequestBuilder
from .requests import RetrieveRequestBuilder
from .requests import SearchRequestBuilder


class ScimService:
    MEDIA_TYPE_SCIM_TYPE = MEDIA_TYPE_SCIM

    def __init__(self, base_url):
        self.base_url = base_url
        self.service_provider_config = None

    def get_service_provider_config(self):
        if not self.service_provider_config:
            self.service_provider_config = self.retrieve(
                SERVICE_PROVIDER_CONFIG_ENDPOINT
            )
        return self.service_provider_config

    def get_resource_types(self):
        return self.search(RESOURCE_TYPES_ENDPOINT).invoke()

    def get_resource_type(self, name):
        return self.retrieve(RESOURCE_TYPES_ENDPOINT, name).invoke()

    def get_schemas(self):
        return self.search(SCHEMAS_ENDPOINT).invoke()

    def get_schema(self, id):
        return self.retrieve(SCHEMAS_ENDPOINT, id).invoke()

    def retrieve(self, endpoint, id):
        endpoint = urljoin(self.base_url, endpoint)
        return RetrieveRequestBuilder(endpoint, id)

    def search(self, endpoint):
        endpoint = urljoin(self.base_url, endpoint)
        return SearchRequestBuilder(endpoint)

    def create(self, endpoint, data):
        endpoint = urljoin(self.base_url, endpoint)
        return CreateRequestBuilder(endpoint, data)

    def modify(self, endpoint, id):
        endpoint = urljoin(self.base_url, endpoint)
        return ModifyRequestBuilder(endpoint, id)

    def replace(self, endpoint, id, data):
        endpoint = urljoin(self.base_url, endpoint)
        return ReplaceRequestBuilder(endpoint, id, data)

    def delete(self, endpoint, id):
        endpoint = urljoin(self.base_url, endpoint)
        return DeleteRequestBuilder(endpoint, id)
