#!/usr/bin/env python3
from scim_server.schemas.attribute_names import AttributeNames


class ProtocolAttributeNames:
    BulkOperationIdentifier = "bulkId"
    Count = "count"
    Data = "data"
    Detail = "detail"
    ErrorType = "scimType"
    ExcludedAttributes = "excludedAttributes"
    FailOnErrors = "failOnErrors"
    ItemsPerPage = "itemsPerPage"
    Location = "location"
    Method = "method"
    Operations = "Operations"
    Patch1Operation = "operation"
    Patch2Operation = "op"
    Path = AttributeNames.Path
    Reference = "$ref"
    Resources = "Resources"
    Response = "response"
    Schemas = "schemas"
    SortBy = "sortBy"
    SortOrder = "sortOrder"
    StartIndex = "startIndex"
    Status = "status"
    TotalResults = "totalResults"
