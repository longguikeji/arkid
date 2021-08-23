from openapi.utils import extend_schema_tags

tag = 'subuser'
path = tag
name = '子账号管理'

extend_schema_tags(
    tag,
    name
)