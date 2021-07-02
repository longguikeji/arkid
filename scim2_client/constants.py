#!/usr/bin/env python3

SERVICE_PROVIDER_CONFIG_ENDPOINT = "ServiceProviderConfig"

# An HTTP GET to this endpoint is used to discover the types of
# resources available on a SCIM service provider (for example, Users and
# Groups).
RESOURCE_TYPES_ENDPOINT = "ResourceTypes"

# An HTTP GET to this endpoint is used to retrieve information about
# resource schemas supported by a SCIM service provider.
SCHEMAS_ENDPOINT = "Schemas"

# The "{@code /Me}" authenticated subject URI alias for the User or other resource
# associated with the currently authenticated subject for any SCIM operation.
ME_ENDPOINT = "Me"

# An HTTP POST to this endpoint is used to retrieve information about
# resource schemas supported by a SCIM service provider.
SEARCH_WITH_POST_PATH_EXTENSION = ".search"

# The SCIM media type string.
MEDIA_TYPE_SCIM = "application/scim+json"

# The HTTP query parameter used in a URI to exclude specific SCIM attributes.
QUERY_PARAMETER_EXCLUDED_ATTRIBUTES = "excludedAttributes"

# The HTTP query parameter used in a URI to include specific SCIM attributes.
QUERY_PARAMETER_ATTRIBUTES = "attributes"

# The HTTP query parameter used in a URI to provide a filter expression.
QUERY_PARAMETER_FILTER = "filter"

# The HTTP query parameter used in a URI to sort by a SCIM attribute.
QUERY_PARAMETER_SORT_BY = "sortBy"

# The HTTP query parameter used in a URI to specify the sort order.
QUERY_PARAMETER_SORT_ORDER = "sortOrder"

# The HTTP query parameter used in a URI to specify the starting index
# for page results.
QUERY_PARAMETER_PAGE_START_INDEX = "startIndex"

# The HTTP query parameter used in a URI to specify the maximum size of
# a page of results.
QUERY_PARAMETER_PAGE_SIZE = "count"
