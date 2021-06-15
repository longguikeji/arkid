from openapi.utils import extend_schema_tags

tag = 'register_config'
path = tag
name = '注册配置'

extend_schema_tags(
    tag,
    name
)