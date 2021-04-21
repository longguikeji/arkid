from openapi.utils import extend_schema_tags

tag = 'user'
path = tag
name = '用户列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/',
                'method': 'post'
            },
            'export': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                'method': 'get'
            },
            'import': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                'method': 'post'
            }
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{id}/',
                'method': 'delete'
            }
        }
    }
)