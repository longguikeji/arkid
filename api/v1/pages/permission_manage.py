from openapi.utils import extend_schema_tags

tag = 'permission_manage'
path = tag
name = '权限管理'

extend_schema_tags(
    tag,
    name
)