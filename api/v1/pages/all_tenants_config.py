from openapi.utils import extend_schema_tags

tag = 'all_tenants_config'
path = tag
name = '租户设置'

extend_schema_tags(
    tag,
    name
)