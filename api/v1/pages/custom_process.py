from openapi.utils import extend_schema_tags

tag = 'custom_process'
path = tag
name = '自定义流程'

extend_schema_tags(
    tag,
    name
)