from openapi.utils import extend_schema_tags

tag = 'third_login'
path = tag
name = '第三方登录配置'

extend_schema_tags(
    tag,
    name
)