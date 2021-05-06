#!/usr/bin/env python3


import requests
from .base_request_builder import BaseRequestBuilder


class ModifyRequestBuilder(BaseRequestBuilder):
    def __init__(self, endpoint, id):
        super().__init__(self, endpoint, id)
        self.version = None
        self.operations = []

    def if_match(self, version):
        self.version = version

    def build_data(self):
        data = {
            'schemas': ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            'Operations': self.operations,
        }
        return data

    def replace_value(self, path, value):
        if not path:
            assert isinstance(value, dict), 'value must be a dict if path is null'
        self.add_operation({'op': 'replace', 'path': path, 'value': value})

    def add_value(self, path, value):
        if not path:
            assert isinstance(value, dict), 'value must be a dict if path is null'
        self.add_operation({'op': 'add', 'path': path, 'value': value})

    def remove_value(self, path):
        if not path:
            raise Exception('No path specified!')
        self.add_operation({'op': 'remove', 'path': path})

    def add_operation(self, operation):
        self.opertions.append(operation)
        return self

    def invoke(self):
        if not self.operations:
            raise Exception('No operations specified!')

        if self.version:
            self.headers['If-Match'] = self.version

        data = self.build_data()
        r = requests.patch(self.base_url, data=data, headers=self.headers)
        return r.status_code, r.text
