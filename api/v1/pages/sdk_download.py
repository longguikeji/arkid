from openapi.utils import extend_schema_tags

tag = 'sdk_download'
path = tag
name = 'SDK下载'

extend_schema_tags(
    tag,
    name
)