from openapi.utils import extend_schema_tags

tag = 'sub_admin_config'
path = tag
name = '子管理员设置'

extend_schema_tags(
    tag,
    name
)