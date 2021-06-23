from openapi.utils import extend_schema_tags

tag = 'all_tenants'
path = tag
name = '租户列表'

extend_schema_tags(
    tag,
    name
)