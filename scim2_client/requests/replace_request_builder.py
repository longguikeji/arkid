#!/usr/bin/env python3


import requests
from .base_request_builder import BaseRequestBuilder


class ReplaceRequestBuilder(BaseRequestBuilder):
    def __init__(self, session, endpoint, id, data):
        super().__init__(session, endpoint, id=id, data=data)
        self.version = None

    def if_match(self, version):
        self.version = version

    def invoke(self):
        if self.version:
            self.headers['If-Match'] = self.version

        r = self.session.put(self.base_url, json=self.data, headers=self.headers)
        return r.status_code, r.text
