from openapi.utils import extend_schema_tags

tag = 'data_synchronism'
path = tag
name = '数据同步'

extend_schema_tags(
    tag,
    name
)