from openapi.utils import extend_schema_tags

tag = 'tenant'
path = tag
name = '租户管理'


extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/',
                'method': 'post'
            }
        }
    }
)