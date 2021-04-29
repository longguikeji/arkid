#!/usr/bin/env python3

import requests
from .base_request_builder import BaseRequestBuilder


class CreateRequestBuilder(BaseRequestBuilder):
    def __init__(self, endpoint, data):
        super().__init__(self, endpoint, data=data)

    def invoke(self):
        r = requests.post(self.base_url, data=self.data, headers=self.headers)
        return r.status_code, r.text
