from openapi.utils import extend_schema_tags

tag = 'other_factor'
path = tag
name = '其他因素'

extend_schema_tags(
    tag,
    name
)