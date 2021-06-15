from openapi.utils import extend_schema_tags

tag = 'log'
path = tag
name = '日志列表'

extend_schema_tags(
    tag,
    name
)