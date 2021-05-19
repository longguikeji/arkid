#!/usr/bin/env python3
from urllib.parse import urljoin


class BaseRequestBuilder:
    def __init__(self, endpoint, id=None, data=None):
        self.base_url = urljoin(endpoint, str(id) if id else '')
        self.headers = {"Accept": "application/json, application/scim+json"}
        self.params = {}
        self.data = data
        self.attributes = []
        self.is_excluded = False

    def add_header(self, key, value):
        self.headers[key] = value
        return self

    def add_param(self, key, value):
        self.params[key] = value
        return self

    def add_attr(self, value):
        self.attributes.append(value)

    def add_excluded_attr(self, value):
        self.attributes.append(value)
        self.is_excluded = True

    def invoke(self):
        if self.attributes:
            if self.is_excluded:
                self.headers['excludedAttributes'] = ','.join(self.attributes)
            else:
                self.headers['attributes'] = ','.join(self.attributes)
