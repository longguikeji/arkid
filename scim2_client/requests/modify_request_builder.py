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
        pass

    def replace_value(self, path, value):
        pass

    def add_value(self, path, values):
        pass

    def remove_value(self, path):
        pass

    def add_operation(self, operation):
        self.opertions.append(operation)
        return self

    def invoke(self):
        if self.version:
            self.headers['If-Match'] = self.version

        data = self.build_data()
        r = requests.patch(self.base_url, data=data, headers=self.headers)
        return r.status_code, r.text
