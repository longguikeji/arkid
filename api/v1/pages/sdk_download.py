from openapi.utils import extend_schema_tags

tag = 'sdk'
path = tag
name = 'SDK下载'

extend_schema_tags(
    tag,
    name
)