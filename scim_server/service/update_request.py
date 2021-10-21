#!/usr/bin/env python3

from scim_server.service.scim_request import ScimRequest


class UpdateRequest(ScimRequest):
    def __init__(self, request, payload, correlation_identifier, extensions):
        super().__init__(request, payload, correlation_identifier, extensions)
