from openapi.utils import extend_schema_tags

tag = 'scan_code'
path = tag
name = '扫码登录'

extend_schema_tags(
    tag,
    name
)