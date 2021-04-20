from openapi.utils import extend_schema_tags

tag = 'group'
path = tag
name = '分组管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'tree_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/',
                'method': 'post'
            }
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/{id}/',
                'method': 'delete'
            },
            'children': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/group/?parent={id}',
                'method': 'get'
            }
        },
        'table': {
            'init': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/user/?group={id}',
                'method': 'get'
            },
            'page': {
                'export': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_export/',
                    'method': 'get'
                },
                'import': {
                    'path': '/api/v1/tenant/{parent_lookup_tenant}/user/user_import/',
                    'method': 'post'
                }
            }
        }
    }
)