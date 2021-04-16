from openapi.utils import extend_schema_tags

tag = 'maketplace'
path = tag
name = '插件市场'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/marketplace/',
            'method': 'get'
        },
        'retrieve': {
            'path': '/api/v1/marketplace/',
            'method': 'get'
        },
    }
)