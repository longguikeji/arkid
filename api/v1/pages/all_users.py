from openapi.utils import extend_schema_tags

tag = 'all_users'
path = tag
name = '用户列表'

extend_schema_tags(
    tag,
    name
)