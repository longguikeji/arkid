from openapi.utils import extend_schema_tags

tag = 'tenant_config'
path = tag
name = '租户配置'

extend_schema_tags(
    tag,
    name
)