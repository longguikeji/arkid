from openapi.utils import extend_schema_tags

tag = 'arkstore'
path = tag
name = '插件商店'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/arkstore/',
            'method': 'get'
        }
    }
)