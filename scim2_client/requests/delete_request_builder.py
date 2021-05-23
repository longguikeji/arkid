#!/usr/bin/env python3
import requests
from .base_request_builder import BaseRequestBuilder


class DeleteRequestBuilder(BaseRequestBuilder):
    def __init__(self, session, endpoint, id):
        super().__init__(session, endpoint, id)
        self.version = None

    def if_match(self, version):
        self.version = version

    def invoke(self):
        super().invoke()
        if self.version:
            self.headers['If-Match'] = self.version

        r = self.session.delete(self.base_url, headers=self.headers)
        return r.status_code, r.text
