#!/usr/bin/env python3
#
class ProtocolSchemaIdentifiers:
    Error = "Error"

    OperationPatch = "PatchOp"

    VersionMessages2 = "2.0:"

    PrefixMessages = "urn:ietf:params:scim:api:messages:"
    PrefixMessages2 = PrefixMessages + VersionMessages2

    ResponseList = "ListResponse"
    RequestBulk = "BulkRequest"

    ResponseBulk = "BulkResponse"

    Version2Error = PrefixMessages2 + Error

    Version2ListResponse = PrefixMessages2 + ResponseList

    Version2PatchOperation = PrefixMessages2 + OperationPatch
    Version2BulkRequest = PrefixMessages2 + RequestBulk

    Version2BulkResponse = PrefixMessages2 + ResponseBulk
