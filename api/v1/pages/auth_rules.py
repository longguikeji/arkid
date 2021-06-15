from openapi.utils import extend_schema_tags

tag = 'auth_rules'
path = tag
name = '认证规则'

extend_schema_tags(
    tag,
    name
)