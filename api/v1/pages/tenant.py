from openapi.utils import extend_schema_tags

tag = 'tenant'
path = tag
name = '租户管理'


extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{id}/',
            'method': 'delete'
        }
    }
)