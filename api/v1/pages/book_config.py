from openapi.utils import extend_schema_tags

tag = 'book_config'
path = tag
name = '通讯录设置'

extend_schema_tags(
    tag,
    name
)