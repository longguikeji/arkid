#!/usr/bin/env python3
import requests
from .base_request_builder import BaseRequestBuilder


class DeleteRequestBuilder(BaseRequestBuilder):
    def __init__(self, endpoint, id):
        super().__init__(self, endpoint, id)
        this.version = None

    def if_match(self, version):
        this.version = version

    def invoke(self):
        super().invoke()
        if self.version:
            self.headers['If-Match'] = self.version

        r = requests.delete(self.base_url, headers=self.headers)
        return r.status_code, r.text
