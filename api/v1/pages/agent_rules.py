from openapi.utils import extend_schema_tags

tag = 'agent_rules'
path = tag
name = '代理规则'

extend_schema_tags(
    tag,
    name
)