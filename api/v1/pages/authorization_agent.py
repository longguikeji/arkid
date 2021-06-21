from openapi.utils import extend_schema_tags

tag = 'authorization_agent'
path = tag
name = '身份源代理'

extend_schema_tags(
    tag,
    name
)