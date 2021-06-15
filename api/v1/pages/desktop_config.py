from openapi.utils import extend_schema_tags

tag = 'desktop_config'
path = tag
name = '桌面设置'

extend_schema_tags(
    tag,
    name
)