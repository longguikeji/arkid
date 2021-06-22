from openapi.utils import extend_schema_tags

tag = 'all_users_config'
path = tag
name = '用户设置'

extend_schema_tags(
    tag,
    name
)