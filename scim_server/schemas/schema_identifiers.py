#!/usr/bin/env python3
from scim_server.schemas.types import Types


class SchemaIdentifiers:
    Extension = 'extension:'
    ExtensionEnterprise2 = Extension + 'enterprise:2.0:'
    NULL = '/'

    PrefixTypes1 = 'urn:scim:schemas:'
    PrefixTypes2 = 'urn:ietf:params:scim:schemas:'

    VersionSchemasCore2 = 'core:2.0:'

    Core2EnterpriseUser = PrefixTypes2 + ExtensionEnterprise2 + Types.User
    Core2Group = PrefixTypes2 + VersionSchemasCore2 + Types.Group

    Core2ResourceType = PrefixTypes2 + ExtensionEnterprise2 + Types.ResourceType

    Core2ServiceConfiguration = (
        PrefixTypes2 + VersionSchemasCore2 + Types.ServiceProviderConfiguration
    )

    Core2User = PrefixTypes2 + VersionSchemasCore2 + Types.User

    Core2Schema = PrefixTypes2 + VersionSchemasCore2 + Types.Schema

    PrefixExtension = PrefixTypes2 + Extension
