from openapi.utils import extend_schema_tags

tag = 'security'
path = tag
name = '安全设置'

extend_schema_tags(
    tag,
    name
)