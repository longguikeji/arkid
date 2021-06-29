from openapi.utils import extend_schema_tags

tag = 'tenant_config'
path = tag
name = '租户配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'delete'
            }   
        }
    }
)