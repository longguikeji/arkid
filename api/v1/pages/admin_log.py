from openapi.utils import extend_schema_tags

tag = 'admin_log'
path = tag
name = '管理员行为日志'

extend_schema_tags(
    tag,
    name
)