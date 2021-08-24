from openapi.utils import extend_schema_tags

tag = 'user_log'
path = tag
name = '用户行为日志'

extend_schema_tags(
    tag,
    name
)