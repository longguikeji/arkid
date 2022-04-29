#!/usr/bin/env python3
from scim_server.protocol.patch_operation2_base import PatchOperation2Base


class PatchRequest2(PatchOperation2Base):
    def __init__(self, operations):
        super().__init__(operations)
