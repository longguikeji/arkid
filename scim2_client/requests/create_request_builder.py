#!/usr/bin/env python3

import requests
from .base_request_builder import BaseRequestBuilder


class CreateRequestBuilder(BaseRequestBuilder):
    def __init__(self, session, endpoint, data):
        super().__init__(session, endpoint, data=data)

    def invoke(self):
        r = self.session.post(self.base_url, json=self.data, headers=self.headers)
        return r.status_code, r.text
