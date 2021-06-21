from openapi.utils import extend_schema_tags

tag = 'statistics'
path = tag
name = '统计图表'

extend_schema_tags(
    tag,
    name
)