#!/usr/bin/env python3
from scim_server.schemas.schema_constants import SchemaConstants


class ProtocolConstants:
    ContentType = "application/scim+json"
    PathGroups = "Groups"
    PathUsers = "Users"
    PathBulk = "Bulk"
    PathWebBatchInterface = SchemaConstants.PathInterface + "/batch"
