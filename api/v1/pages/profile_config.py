from openapi.utils import extend_schema_tags

tag = 'profile_config'
path = tag
name = '个人资料设置'

extend_schema_tags(
    tag,
    name
)