#!/usr/bin/env python3


import requests
from .base_request_builder import BaseRequestBuilder


class ReplaceRequestBuilder(BaseRequestBuilder):
    def __init__(self, endpoint, id, data):
        super().__init__(self, endpoint, id=id, data=data)
        this.version = None

    def if_match(self, version):
        this.version = version

    def invoke(self):
        if self.version:
            self.headers['If-Match'] = self.version

        r = requests.put(self.base_url, data=self.data, headers=self.headers)
        return r.status_code, r.text
