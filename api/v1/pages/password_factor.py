from openapi.utils import extend_schema_tags

tag = 'password_factor'
path = tag
name = '密码管理'

extend_schema_tags(
    tag,
    name
)