from openapi.utils import extend_schema_tags

tag = 'scan'
path = tag
name = '扫码登录'

extend_schema_tags(
    tag,
    name
)