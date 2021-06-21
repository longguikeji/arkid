from openapi.utils import extend_schema_tags

tag = 'permission_group'
path = tag
name = '权限分组'

extend_schema_tags(
    tag,
    name
)