#!/usr/bin/env python3
from scim_server.exceptions import ArgumentNullException


class Patch:
    def __init__(self, resource_identifier, request):
        if not request:
            raise ArgumentNullException('request')
        self.resource_identifier = resource_identifier
        self.patch_request = request
