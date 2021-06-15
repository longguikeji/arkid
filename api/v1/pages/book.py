from openapi.utils import extend_schema_tags

tag = 'book'
path = tag
name = '通讯录'

extend_schema_tags(
    tag,
    name
)