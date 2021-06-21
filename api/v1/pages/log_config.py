from openapi.utils import extend_schema_tags

tag = 'log_config'
path = tag
name = '日志设置'

extend_schema_tags(
    tag,
    name
)